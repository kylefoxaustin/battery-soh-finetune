"""EXPLORATORY (reviewer's own re-implementation of the convsim loss model, CC0 source read
and transcribed; not an import of repo code). Question: how does the 'static table by load
suffices' verdict in results/X/convsim depend on the hard-switching energy per transition?
Scales EOSS (and QOSS ~ sqrt) on the SAME 48->12 V buck model with the same WLTC load.
This is NOT an 800 V DAB model. It asks only whether the verdict is a property of the plant.
"""
import sys, numpy as np

V_IN, V_OUT = 48.0, 12.0
D = V_OUT / V_IN
RDS_25, TC_RDS = 0.0032, 0.0065
QOSS0, EOSS0 = 30e-9, 0.75e-6
QG, VDRV, V_SD = 10e-9, 5.0, 2.0
L_PH0, R_DCR = 1.0e-6, 0.0012
K_CORE, P_FIX, P_PH = 2.672e-04, 1.5, 0.25
N_GRID = np.arange(1, 7)
F_GRID = np.array([150e3, 250e3, 400e3, 600e3, 900e3, 1.3e6])
TD_GRID = np.array([5e-9, 10e-9, 20e-9, 35e-9, 55e-9])
GRID = [(n, f, td) for n in N_GRID for f in F_GRID for td in TD_GRID]

P = dict(EOSS=EOSS0, QOSS=QOSS0, L_PH=L_PH0)


def loss(I, Tj, age, n, f, td):
    rds = RDS_25 * (1 + TC_RDS * (Tj - 25)) * (1 + 0.30 * age)
    qoss = P['QOSS'] * (1 + 0.15 * age)
    Iph = I / n
    dI = (V_IN - V_OUT) * D / (P['L_PH'] * f)
    Irms2 = Iph ** 2 + dI ** 2 / 12.0
    p_cond = Irms2 * (rds + R_DCR)
    I_valley = Iph - dI / 2
    I_avail = max(abs(I_valley), 1e-3)
    t_swing = 2 * qoss / I_avail
    hard = max(0.0, 1 - td / t_swing) if I_valley < 0 else 1.0
    p_sw_on = hard * P['EOSS'] * f + 0.5 * V_IN * Iph * 2e-9 * f * (I_valley >= 0)
    p_dead = V_SD * Iph * 2 * max(td - t_swing, 0.0) * f
    p_core = K_CORE * (f / 1e5) ** 1.35 * dI ** 2.1
    p_gate = 2 * QG * VDRV * f
    return n * (p_cond + p_sw_on + p_dead + p_core + p_gate + P_PH) + P_FIX


def best(I, Tj, age):
    return min(GRID, key=lambda g: loss(I, Tj, age, *g))


v_kmh = np.load(sys.argv[1], allow_pickle=False)
T = len(v_kmh); dt = 1.0
m, Cd, A, Crr, rho, g = 1900.0, 0.27, 2.3, 0.009, 1.2, 9.81
v = v_kmh / 3.6; a = np.gradient(v, dt)
P_trac = (m * a + 0.5 * rho * Cd * A * v ** 2 + Crr * m * g * (v > 0.1)) * v
k = np.arange(T)
P_load = np.clip(350.0 + 0.006 * np.abs(P_trac) + 180.0 * (np.sin(2 * np.pi * k / 97.0) > 0.35)
                 + np.where(np.abs(np.gradient(v_kmh)) > 1.5, 420.0, 0.0), 120.0, 2400.0)
I_load = P_load / V_OUT


def thermal(P_loss, T_amb, Rth=1.1, tau=35.0):
    out = np.empty_like(P_loss); x = T_amb + 10
    for i, p in enumerate(P_loss):
        x += (T_amb + Rth * p - x) * (dt / tau); out[i] = x
    return out


def replay(age, T_amb, noise=1.5, seed=0):
    rng = np.random.default_rng(seed)
    Tj = np.full(T, T_amb + 10.0)
    for _ in range(3):
        Lo = np.array([loss(I_load[i], Tj[i], age, *best(I_load[i], Tj[i], age)) for i in range(T)])
        Tj = thermal(Lo, T_amb)
    Tm = Tj + rng.normal(0, noise, T)
    tbl = {}

    def chS(i):
        key = max(round(I_load[i] / 2.0) * 2.0, 2.0)
        if key not in tbl: tbl[key] = best(key, 60.0, 0.0)
        return tbl[key]

    def chA(i):
        return best(I_load[i], Tm[i], age)

    res = {}
    for name, f in (('oracle', lambda i: best(I_load[i], Tj[i], age)), ('tierA', chA), ('static', chS)):
        L = np.array([loss(I_load[i], Tj[i], age, *f(i)) for i in range(T)])
        res[name] = (P_load.sum() / (P_load.sum() + L.sum()), L.sum())
    return res


print("EOSS_x  Lph_x  age  oracle_eff%  static_eff%  tierA_eff%  excess_static%  eff_pts_lost_static")
for es in (1, 10, 30, 100):
    for lph, age in ((1.0, 0.5), (0.85, 0.5), (1.15, 0.5), (1.0, 1.0)):
        P['EOSS'] = EOSS0 * es; P['QOSS'] = QOSS0 * np.sqrt(es); P['L_PH'] = L_PH0 * lph
        r = replay(age, 45.0)
        ex_s = 100 * (r['static'][1] / r['oracle'][1] - 1)
        print(f"{es:>6}  {lph:5.2f}  {age:3.1f}  {100*r['oracle'][0]:10.3f}  {100*r['static'][0]:10.3f}  "
              f"{100*r['tierA'][0]:9.3f}  {ex_s:13.2f}  {100*(r['oracle'][0]-r['static'][0]):12.3f}")
