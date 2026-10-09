"""Shared model + feature definitions. Imported on the host AND on the board — keep it numpy/torch only.

CHOSEN inputs (brief §0.5) live here as named constants so every result can cite them.
"""
import numpy as np
import torch
import torch.nn as nn

# ---- features -------------------------------------------------------------------------------
# Raw EVBattery columns: 0 avgV, 1 current, 2 SOC, 3 maxV, 4 minV, 5 maxT, 6 minT, 7 time[s]
RAW_COLS = [0, 1, 2, 3, 4, 5, 6]          # time dropped (snippets are uniformly 10 s)
ROLL_COLS = [0, 1, 5]                     # rolling mean/std on avgV, current, maxT (brief §3)
ROLL_WIN = 8                              # CHOSEN: 8 samples = 80 s
SEQ_LEN = 128                             # IMPOSED by the dataset (snippet length)
Z_CLIP = 6.0                              # CHOSEN: z-features clipped to ±6 (sensor glitches gave rolling-var
                                          # z up to 180, which wrecked int8 per-tensor input quantization)
MILEAGE_SCALE = 1e5                       # km -> O(1); odometer broadcast as one constant channel
N_FEAT = len(RAW_COLS) + 2 * len(ROLL_COLS) + 1  # 14 (incl. mileage)

# ---- model ----------------------------------------------------------------------------------
HIDDEN = 128      # CHOSEN
LAYERS = 2        # CHOSEN
HEAD_HIDDEN = 64  # CHOSEN


def _rolling(x, w):
    """Causal rolling mean/var along time axis of [N, T, C] (window shrinks at the start)."""
    c = np.cumsum(x, axis=1, dtype=np.float64)
    c2 = np.cumsum(x.astype(np.float64) ** 2, axis=1)
    c = np.concatenate([np.zeros_like(c[:, :1]), c], axis=1)
    c2 = np.concatenate([np.zeros_like(c2[:, :1]), c2], axis=1)
    t = np.arange(1, x.shape[1] + 1)
    lo = np.maximum(t - w, 0)
    n = (t - lo)[None, :, None]
    m = (c[:, t] - c[:, lo]) / n
    v = (c2[:, t] - c2[:, lo]) / n - m ** 2
    return m.astype(np.float32), np.maximum(v, 0).astype(np.float32)


def make_features(X, mileage):
    """X: raw [N, 128, 8], mileage: [N] km -> [N, 128, N_FEAT] float32 (unnormalised).

    Odometer is an input because a BMS knows it, and without it a snippet-only model loses to a
    mileage-only linear fit (measured on ds1 val cars: LSTM 1.61 Ah vs mileage-linear 1.29 Ah) —
    a weak fleet model would flatter every per-vehicle fine-tune in E4."""
    base = X[:, :, RAW_COLS]
    m, v = _rolling(X[:, :, ROLL_COLS], ROLL_WIN)
    v = np.sqrt(v)  # std, not var: compresses the heavy tail
    km = np.broadcast_to((np.asarray(mileage, np.float32) / MILEAGE_SCALE)[:, None, None], (len(X), X.shape[1], 1))
    return np.concatenate([base, m, v, km], axis=2).astype(np.float32)


class Norm:
    """Per-feature z-score + target scaling, fitted on fleet TRAIN cars only, shipped with the model."""

    def __init__(self, mu=None, sd=None, y_mu=None, y_sd=None):
        self.mu, self.sd, self.y_mu, self.y_sd = mu, sd, y_mu, y_sd

    def fit(self, F, y):
        self.mu = F.reshape(-1, F.shape[-1]).mean(0).astype(np.float32)
        self.sd = (F.reshape(-1, F.shape[-1]).std(0) + 1e-6).astype(np.float32)
        self.y_mu, self.y_sd = float(y.mean()), float(y.std())
        return self

    def x(self, F):
        return np.clip((F - self.mu) / self.sd, -Z_CLIP, Z_CLIP).astype(np.float32)

    def y(self, y):
        return ((y - self.y_mu) / self.y_sd).astype(np.float32)

    def y_inv(self, z):
        return z * self.y_sd + self.y_mu

    def state(self):
        return {"mu": self.mu.tolist(), "sd": self.sd.tolist(), "y_mu": self.y_mu, "y_sd": self.y_sd}

    @classmethod
    def from_state(cls, s):
        return cls(np.array(s["mu"], np.float32), np.array(s["sd"], np.float32), s["y_mu"], s["y_sd"])


class SoHNet(nn.Module):
    """backbone = LSTM stack; head = Linear-ReLU-Linear. `head.2` is THE 'last layer'."""

    def __init__(self, n_feat=N_FEAT, hidden=HIDDEN, layers=LAYERS, head_hidden=HEAD_HIDDEN):
        super().__init__()
        self.backbone = nn.LSTM(n_feat, hidden, num_layers=layers, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hidden, head_hidden), nn.ReLU(), nn.Linear(head_hidden, 1))

    def embed(self, x):
        out, _ = self.backbone(x)
        return out[:, -1]

    def forward(self, x):
        return self.head(self.embed(x)).squeeze(-1)


def trainable_params(model, scope):
    """scope: 'full' | 'head' | 'last'. Freezes everything else (requires_grad=False)."""
    for p in model.parameters():
        p.requires_grad = scope == "full"
    if scope == "head":
        for p in model.head.parameters():
            p.requires_grad = True
    elif scope == "last":
        for p in model.head[2].parameters():
            p.requires_grad = True
    return [p for p in model.parameters() if p.requires_grad]


def count(params):
    return sum(p.numel() for p in params)
