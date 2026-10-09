"""DERIVED upper bound on the TFLite activation arena: bytes of every non-constant tensor (op outputs,
graph input, LSTM state variables). The real arena is <= this (TFLite reuses buffers). Not a measurement.

Usage: python model/arena_bound.py runs/ds1/soh_int8.tflite
"""
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402

for path in sys.argv[1:]:
    it = tf.lite.Interpreter(model_path=path)
    it.allocate_tensors()
    written = {o for op in it._get_ops_details() for o in op["outputs"]} | {d["index"] for d in it.get_input_details()}
    variables = {i for op in it._get_ops_details() if op["op_name"] == "UNIDIRECTIONAL_SEQUENCE_LSTM"
                 for i in op["inputs"][18:20]}  # input_activation_state, input_cell_state
    nb = lambda t: int(np.prod(t["shape"])) * np.dtype(t["dtype"]).itemsize  # noqa: E731
    act = sum(nb(t) for t in it.get_tensor_details() if t["index"] in written | variables)
    const = sum(nb(t) for t in it.get_tensor_details() if t["index"] not in written | variables)
    print(json.dumps({"model": os.path.basename(path), "tag": "DERIVED",
                      "nonconstant_tensor_bytes": act, "constant_tensor_bytes": const,
                      "lstm_state_bytes": sum(nb(t) for t in it.get_tensor_details() if t["index"] in variables)}))
