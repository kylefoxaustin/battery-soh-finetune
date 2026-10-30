"""Converter-side efficiency replay — public domain (CC0).

Question: over a real drive cycle, how much converter efficiency does a static
or slowly-updated parameter set leave behind versus continuous on-board
re-optimisation?

Plant (ASSUMED, representative datasheet-class values, no specific product):
  48 V -> 12 V interleaved multiphase buck with GaN half-bridges, 1..6 phases.
  This is the LV DC-DC stage in 48 V vehicle architectures and is physically
  the same problem as a multiphase GaN point-of-load. Chosen because it is a
  non-isolated topology whose loss model is standard and well documented.

Knobs each controller sets: phase count n, switching frequency fsw, dead-time td.
Loss terms: conduction (Rds(on) with tempco and ageing), inductor DCR, core loss,
gate charge, Coss/turn-on loss when ZVS is not achieved, third-quadrant
dead-time loss, fixed controller overhead.

Controllers (all choose from the same grid):
  oracle : true state every second (ceiling)
  tierA  : measured state refreshed every A s (default 1 s), knows age
  tierB  : refreshed every 30 s from a 30 s mean that is 30 s old, knows age
  static : factory table by load only, built for a NEW part at 60 C
Drive cycle: WLTC class 3b, 1 Hz (JRC wltp repository, EUPL).
"""
import numpy as np, json, os

V_IN, V_OUT = 48.0, 12.0
D = V_OUT / V_IN

# ---- device / passive values (ASSUMED) -------------------------------------
RDS_25  = 0.0032   # ohm per switch, 100 V-class GaN, 25 C, new
TC_RDS  = 0.0065   # per C
QOSS    = 30e-9    # C  at 48 V
EOSS    = 0.75e-6  # J  per switch at 48 V
QG      = 10e-9    # C  gate charge
VDRV    = 5.0      # V  gate drive
V_SD    = 2.0      # V  third-quadrant drop
L_PH    = 1.0e-6   # H  per phase
R_DCR   = 0.0012   # ohm per phase inductor
K_CORE  = 2.672e-04 # W, calibrated: ~1.2 W at 400 kHz / 22.5 A ripple (ferrite, ASSUMED)
P_FIX   = 1.5      # W  controller + sensing per converter
P_PH    = 0.25     # W  per active phase (driver quiescent, current sense)

N_GRID  = np.arange(1, 7)
F_GRID  = np.array([150e3, 250e3, 400e3, 600e3, 900e3, 1.3e6])
TD_GRID = np.array([5e-9, 10e-9, 20e-9, 35e-9, 55e-9])

def loss(I, Tj, age, n, f, td):
    rds = RDS_25 * (1 + TC_RDS*(Tj - 25)) * (1 + 0.30*age)   # +30 % Rds at EOL
    qoss = QOSS * (1 + 0.15*age)
    Iph = I / n
    dI = (V_IN - V_OUT) * D / (L_PH * f)
    Irms2 = Iph**2 + dI**2 / 12.0
    p_cond = Irms2 * (rds + R_DCR)                  # one switch conducts at a time
    # Soft switching: the node swings during td using the inductor current at the
    # transition. At light load the valley current can go negative (ZVS on both
    # edges); at heavy load the high-side turns on hard.
    I_valley = Iph - dI/2
    I_avail = max(abs(I_valley), 1e-3)
    t_swing = 2*qoss / I_avail
    if I_valley < 0:          # negative valley current -> both edges soft if td long enough
        hard = max(0.0, 1 - td / t_swing)
    else:                      # positive valley -> high-side turn-on is hard
        hard = 1.0
    p_sw_on  = hard * EOSS * f + 0.5 * V_IN * Iph * 2e-9 * f * (I_valley >= 0)
    p_dead   = V_SD * Iph * 2 * max(td - t_swing, 0.0) * f
    p_core   = K_CORE * (f/1e5)**1.35 * dI**2.1
    p_gate   = 2 * QG * VDRV * f
    return n*(p_cond + p_sw_on + p_dead + p_core + p_gate + P_PH) + P_FIX

_GRID = [(n, f, td) for n in N_GRID for f in F_GRID for td in TD_GRID]
def best(I, Tj, age):
    return min(_GRID, key=lambda g: loss(I, Tj, age, *g))

# ---- drive cycle -> 12 V bus load (ASSUMED vehicle) -------------------------
v_kmh = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wltc3b_kmh.npy'))
T = len(v_kmh); dt = 1.0
m, Cd, A, Crr, rho, g = 1900.0, 0.27, 2.3, 0.009, 1.2, 9.81
v = v_kmh / 3.6; a = np.gradient(v, dt)
P_trac = (m*a + 0.5*rho*Cd*A*v**2 + Crr*m*g*(v > 0.1)) * v
k = np.arange(T)
P_base = 350.0                                            # ECUs, lights, infotainment
P_trac_aux = 0.006 * np.abs(P_trac)                       # pumps/fans tracking power
P_hvac_blower = 180.0 * (np.sin(2*np.pi*k/97.0) > 0.35)   # duty-cycled blower
P_steer = np.where(np.abs(np.gradient(v_kmh)) > 1.5, 420.0, 0.0)  # EPS/brake events
P_load = np.clip(P_base + P_trac_aux + P_hvac_blower + P_steer, 120.0, 2400.0)
I_load = P_load / V_OUT

def thermal(P_loss, T_amb, Rth=1.1, tau=35.0, x0=None):
    out = np.empty_like(P_loss); x = T_amb + 10 if x0 is None else x0
    for i, p in enumerate(P_loss):
        x += (T_amb + Rth*p - x) * (dt / tau); out[i] = x
    return out

def replay(age, T_amb, A_PERIOD=1, B_PERIOD=30, B_DELAY=30, noise=1.5, seed=0):
    rng = np.random.default_rng(seed)
    Tj = np.full(T, T_amb + 10.0)
    for _ in range(3):                    # settle the true Tj under oracle losses
        Lo = np.array([loss(I_load[i], Tj[i], age, *best(I_load[i], Tj[i], age)) for i in range(T)])
        Tj = thermal(Lo, T_amb)
    Tm = Tj + rng.normal(0, noise, T)     # measured junction estimate
    def score(choose):
        L = np.array([loss(I_load[i], Tj[i], age, *choose(i)) for i in range(T)])
        return float(P_load.sum() / (P_load.sum() + L.sum())), L
    cA, cB, tbl = {}, {}, {}
    def chA(i):
        i0 = (i // A_PERIOD) * A_PERIOD
        if i0 not in cA: cA[i0] = best(I_load[i0], Tm[i0], age)
        return cA[i0]
    def chB(i):
        i0 = (i // B_PERIOD) * B_PERIOD; src = max(i0 - B_DELAY, 0)
        if i0 not in cB:
            sl = slice(max(src - 29, 0), src + 1)
            cB[i0] = best(I_load[sl].mean(), Tm[sl].mean(), age)
        return cB[i0]
    def chS(i):
        key = max(round(I_load[i] / 2.0) * 2.0, 2.0)
        if key not in tbl: tbl[key] = best(key, 60.0, 0.0)
        return tbl[key]
    out = {}
    for name, f in [('oracle', lambda i: best(I_load[i], Tj[i], age)),
                    ('tierA', chA), ('tierB', chB), ('static', chS)]:
        eff, L = score(f); out[name] = (eff, L)
    return out, Tj

if __name__ == '__main__':
    print('load W  p5 %.0f  p50 %.0f  p95 %.0f  max %.0f' % tuple(np.percentile(P_load, [5,50,95,100])))
    for P in (150, 300, 600, 1200, 2000):
        b = best(P/12, 60, 0); e = P / (P + loss(P/12, 60, 0, *b))
        print(f'  {P:5d} W -> n={b[0]} f={b[1]/1e3:.0f}k td={b[2]*1e9:.0f}ns  eff {100*e:.2f}%')
