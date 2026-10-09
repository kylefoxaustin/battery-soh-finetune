"""Export the fleet SoHNet to TFLite int8 (host-side), via a weight-copied tf_keras twin.

PyTorch -> TFLite for an LSTM is fragile, so we rebuild the identical graph in tf_keras (whose
LSTM converts to TFLite's fused UNIDIRECTIONAL_SEQUENCE_LSTM) and copy weights:
  PyTorch weight_ih [4H, in] gate order (i, f, g, o) == Keras kernel [in, 4H] order (i, f, c, o)
  kernel = W_ih.T, recurrent_kernel = W_hh.T, bias = b_ih + b_hh
⚠️ The converted UNIDIRECTIONAL_SEQUENCE_LSTM stores h/c as persistent VARIABLE tensors: without
interpreter.reset_all_variables() before each invoke, every inference starts from the previous
sample's final state (measured: up to 0.52 Ah error on 1 in 256 samples, p90 0.009 Ah — invisible in
the median). Every runner here resets before every invoke.
GATES (export aborts on failure):
  1. Keras fp32 vs PyTorch fp32 on GATE_N held-out snippets: max |diff| (Ah) < 1e-3
  2. int8 TFLite vs PyTorch fp32 on the same snippets: RMSE(int8 - fp32) reported, and the int8
     model's RMSE vs ground truth is recorded so E1 can gate against it.
Outputs: soh_int8.tflite, soh_fp32.tflite, gate_samples.npz (inputs + labels + fp32 preds the board
uses to gate E1), export_report.json.

Usage: python model/export_tflite.py --run runs/ds1
"""
import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # export is CPU-only; never touch the shared GPU
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402
import tf_keras as keras  # noqa: E402
import torch  # noqa: E402

from common import HEAD_HIDDEN, HIDDEN, N_FEAT, SEQ_LEN, Norm, SoHNet, make_features  # noqa: E402

GATE_N = 256   # held-out snippets carried to the board for the E1 same-run gate
REP_N = 500    # representative-dataset size for int8 calibration (fleet TRAIN cars only)


def keras_twin(sd, layers):
    inp = keras.Input(shape=(SEQ_LEN, N_FEAT), batch_size=1)
    h = inp
    for i in range(layers):
        h = keras.layers.LSTM(HIDDEN, return_sequences=i < layers - 1, unroll=False, name=f"lstm{i}")(h)
    h = keras.layers.Dense(HEAD_HIDDEN, activation="relu", name="head0")(h)
    out = keras.layers.Dense(1, name="head2")(h)
    m = keras.Model(inp, out)
    for i in range(layers):
        g = lambda k: sd[f"backbone.{k}_l{i}"].numpy()  # noqa: E731
        m.get_layer(f"lstm{i}").set_weights([g("weight_ih").T, g("weight_hh").T, g("bias_ih") + g("bias_hh")])
    m.get_layer("head0").set_weights([sd["head.0.weight"].numpy().T, sd["head.0.bias"].numpy()])
    m.get_layer("head2").set_weights([sd["head.2.weight"].numpy().T, sd["head.2.bias"].numpy()])
    return m


def run_tflite(path, Xn):
    it = tf.lite.Interpreter(model_path=path)
    it.allocate_tensors()
    i, o = it.get_input_details()[0], it.get_output_details()[0]
    out = []
    for x in Xn:
        x = x[None]
        if i["dtype"] == np.int8:
            s, z = i["quantization"]
            x = np.clip(np.round(x / s + z), -128, 127).astype(np.int8)
        it.reset_all_variables()  # the converted LSTM keeps h/c as VARIABLE tensors across invokes
        it.set_tensor(i["index"], x)
        it.invoke()
        y = it.get_tensor(o["index"]).astype(np.float32)
        if o["dtype"] == np.int8:
            s, z = o["quantization"]
            y = (y - z) * s
        out.append(y.reshape(-1)[0])
    return np.array(out, np.float32), i, o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="runs/ds1")
    a = ap.parse_args()
    split = json.load(open(os.path.join(a.run, "split.json")))
    norm = Norm.from_state(json.load(open(os.path.join(a.run, "norm.json"))))
    model = SoHNet().eval()
    sd = torch.load(os.path.join(a.run, "fleet.pt"), map_location="cpu")
    model.load_state_dict(sd)

    d = np.load(os.path.join(ROOT, f"data/processed/evbattery_ds{split['ds']}.npz"))
    rng = np.random.default_rng(1)
    va_idx = rng.choice(np.flatnonzero(np.isin(d["car"], split["val"])), GATE_N, replace=False)
    tr_idx = rng.choice(np.flatnonzero(np.isin(d["car"], split["train"])), REP_N, replace=False)
    Xg = norm.x(make_features(d["X"][va_idx], d["mileage"][va_idx]))
    yg = d["capacity"][va_idx]
    Xrep = norm.x(make_features(d["X"][tr_idx], d["mileage"][tr_idx]))

    with torch.no_grad():
        p_torch = norm.y_inv(model(torch.from_numpy(Xg)).numpy())
    km = keras_twin(sd, model.backbone.num_layers)
    p_keras = norm.y_inv(np.concatenate([km(Xg[i:i + 1], training=False).numpy().reshape(-1)
                                         for i in range(GATE_N)]))
    keras_maxdiff = float(np.max(np.abs(p_keras - p_torch)))
    assert keras_maxdiff < 1e-3, f"GATE 1 FAIL: keras twin != torch (max diff {keras_maxdiff} Ah)"

    conv = tf.lite.TFLiteConverter.from_keras_model(km)
    fp32_bytes = conv.convert()
    open(os.path.join(a.run, "soh_fp32.tflite"), "wb").write(fp32_bytes)

    conv = tf.lite.TFLiteConverter.from_keras_model(km)
    conv.optimizations = [tf.lite.Optimize.DEFAULT]
    conv.representative_dataset = lambda: ([Xrep[i:i + 1]] for i in range(REP_N))
    conv.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    conv.inference_input_type = tf.int8
    conv.inference_output_type = tf.int8
    int8_bytes = conv.convert()
    p8 = os.path.join(a.run, "soh_int8.tflite")
    open(p8, "wb").write(int8_bytes)

    z8, i8, o8 = run_tflite(p8, Xg)
    p_int8 = norm.y_inv(z8)
    zf, _, _ = run_tflite(os.path.join(a.run, "soh_fp32.tflite"), Xg)
    p_fp32tfl = norm.y_inv(zf)
    fp32_maxdiff = float(np.max(np.abs(p_fp32tfl - p_torch)))
    assert fp32_maxdiff < 1e-3, f"GATE FAIL: fp32 tflite != torch (max diff {fp32_maxdiff} Ah) — LSTM state reset?"

    # ops actually present in the int8 flatbuffer (placement evidence for E1)
    it = tf.lite.Interpreter(model_path=p8)
    ops = sorted({d["op_name"] for d in it._get_ops_details()})

    rmse = lambda p: float(np.sqrt(np.mean((p - yg) ** 2)))  # noqa: E731
    rep = {
        "keras_vs_torch_maxdiff_ah": keras_maxdiff,
        "fp32tflite_vs_torch_maxdiff_ah": float(np.max(np.abs(p_fp32tfl - p_torch))),
        "int8_vs_torch_rmse_ah": float(np.sqrt(np.mean((p_int8 - p_torch) ** 2))),
        "int8_vs_torch_maxdiff_ah": float(np.max(np.abs(p_int8 - p_torch))),
        "rmse_vs_label_ah": {"torch_fp32": rmse(p_torch), "tflite_int8": rmse(p_int8)},
        "bytes": {"int8_tflite": len(int8_bytes), "fp32_tflite": len(fp32_bytes)},
        "int8_ops": ops,
        "io": {"in": [str(i8["dtype"]), list(map(float, i8["quantization"]))],
               "out": [str(o8["dtype"]), list(map(float, o8["quantization"]))]},
        "gate_n": GATE_N, "rep_n": REP_N, "tf": tf.__version__,
    }
    np.savez(os.path.join(a.run, "gate_samples.npz"), Xn=Xg, y=yg, p_torch=p_torch, p_int8_host=p_int8)
    json.dump(rep, open(os.path.join(a.run, "export_report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
