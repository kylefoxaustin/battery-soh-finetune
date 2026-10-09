"""E1 (H1): int8 TFLite inference footprint + latency on the A55, gated in the SAME run.

Fresh process. Order: imports -> rss_pre -> build interpreter + allocate -> rss_alloc ->
GATE pass over all gate samples (outputs kept) -> timed loop on the same samples -> VmHWM.
Gate (brief §0.3), evaluated on the outputs produced IN THIS PROCESS:
  - int8 model: board output == host int8 output (exported alongside) within MAX_LSB_DIFF output LSBs
    fp32 model: board output == PyTorch fp32 output within FP32_TOL_AH
  - RMSE(board vs labels) <= reference RMSE + RMSE_SLACK_AH
Latency/RSS are tagged MEASURED only if the gate passes, else UNGATED.

Latency includes interpreter.reset_all_variables() (the converted LSTM keeps state across invokes).
Interpreter: tflite_runtime if present, else tensorflow.lite (recorded). Runs on the A55 CPU
(XNNPACK/builtin kernels) — the LSTM is not offered to the Neutron NPU (recorded as placement).

Usage: taskset -c 2 python3 board/e1_inference.py --run runs/ds1 --out results/raw/e1.json
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpustat  # noqa: E402
import numpy as np  # noqa: E402

MAX_LSB_DIFF = 1
FP32_TOL_AH = 1e-3
RMSE_SLACK_AH = 0.05
WARMUP, ITERS = 20, 1000  # CHOSEN


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--model", default="soh_int8.tflite")
    ap.add_argument("--threads", type=int, default=1)  # CHOSEN: single-stream, 1 thread
    ap.add_argument("--runtime", choices=["auto", "tflite_runtime", "tf"], default="auto")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.runtime in ("auto", "tflite_runtime"):
        try:
            from tflite_runtime.interpreter import Interpreter
            rt = "tflite_runtime"
        except ImportError:
            if a.runtime == "tflite_runtime":
                raise
            a.runtime = "tf"
    if a.runtime == "tf":
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter
        rt = "tensorflow.lite"
    rss_pre = cpustat.vm_rss_kb()

    path = os.path.join(a.run, a.model)
    it = Interpreter(model_path=path, num_threads=a.threads)
    it.allocate_tensors()
    rss_alloc = cpustat.vm_rss_kb()
    i, o = it.get_input_details()[0], it.get_output_details()[0]
    g = np.load(os.path.join(a.run, "gate_samples.npz"))
    import json
    norm = json.load(open(os.path.join(a.run, "norm.json")))
    quant = i["dtype"] == np.int8
    if quant:
        si, zi = i["quantization"]
        so, zo = o["quantization"]
        Xq = np.clip(np.round(g["Xn"] / si + zi), -128, 127).astype(np.int8)
        ref, lsb_unit = g["p_int8_host"], so * norm["y_sd"]  # int8: compare to host int8, in output LSBs
    else:
        Xq = g["Xn"].astype(np.float32)
        ref, lsb_unit = g["p_torch"], None                    # fp32: compare to PyTorch fp32, in Ah

    # ---- gate pass: outputs produced by THIS process ----
    raw = np.empty(len(Xq), np.float32)
    for k in range(len(Xq)):
        it.reset_all_variables()  # LSTM h/c are persistent variable tensors — reset per inference
        it.set_tensor(i["index"], Xq[k:k + 1])
        it.invoke()
        raw[k] = it.get_tensor(o["index"]).reshape(-1)[0]
    z = (raw - zo) * so if quant else raw
    pred = z * norm["y_sd"] + norm["y_mu"]
    rmse_board = float(np.sqrt(np.mean((pred - g["y"]) ** 2)))
    rmse_ref = float(np.sqrt(np.mean((ref - g["y"]) ** 2)))
    if quant:
        dev = float((np.abs(pred - ref) / lsb_unit).max())
        gate = {"max_lsb_vs_host_int8": dev, "match_ok": dev <= MAX_LSB_DIFF + 1e-3}
    else:
        dev = float(np.abs(pred - ref).max())
        gate = {"max_abs_vs_torch_ah": dev, "match_ok": dev <= FP32_TOL_AH}
    gate.update({"rmse_board_ah": rmse_board, "rmse_ref_ah": rmse_ref,
                 "rmse_ok": rmse_board <= rmse_ref + RMSE_SLACK_AH})
    gate["pass"] = gate["match_ok"] and gate["rmse_ok"]

    # ---- timed loop (same interpreter, same inputs) ----
    for k in range(WARMUP):
        it.reset_all_variables()
        it.set_tensor(i["index"], Xq[k % len(Xq):k % len(Xq) + 1])
        it.invoke()
    cpu = cpustat.CpuSampler().start()
    lat = np.empty(ITERS)
    for k in range(ITERS):
        x = Xq[k % len(Xq):k % len(Xq) + 1]
        t0 = time.perf_counter_ns()
        it.reset_all_variables()  # counted: it is part of a correct single inference
        it.set_tensor(i["index"], x)
        it.invoke()
        it.get_tensor(o["index"])
        lat[k] = (time.perf_counter_ns() - t0) / 1e6
    cpu_res = cpu.stop()
    hwm = cpustat.vm_hwm_kb()

    tag = "MEASURED" if gate["pass"] else "UNGATED"
    ops = sorted({d["op_name"] for d in it._get_ops_details()}) if hasattr(it, "_get_ops_details") else None
    res = {"tag": tag, "runtime": rt, "threads": a.threads, "model": a.model,
           "tflite_bytes": os.path.getsize(path),
           "latency_ms": {"mean": float(lat.mean()), "p50": float(np.percentile(lat, 50)),
                          "p99": float(np.percentile(lat, 99)), "min": float(lat.min()), "n": ITERS},
           "mem_kb": {"rss_pre_interpreter": rss_pre, "rss_after_allocate": rss_alloc,
                      "interp_delta": rss_alloc - rss_pre, "hwm": hwm},
           "placement": {"ops": ops, "delegate": "none (A55 CPU builtin kernels)"},
           "gate": gate, "cpu_pct": cpu_res, "env": cpustat.environment()}
    cpustat.dump(a.out, res)
    print(f"[{tag}] {a.model}: {res['tflite_bytes']} B, p50 {res['latency_ms']['p50']:.3f} ms, "
          f"interp delta {res['mem_kb']['interp_delta']} KB, hwm {hwm} KB, gate {gate}")


if __name__ == "__main__":
    main()
