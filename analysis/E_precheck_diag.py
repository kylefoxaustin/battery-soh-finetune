"""Post-hoc DIAGNOSTIC for the §5 pre-check (does NOT change its decision): in-sample R^2, per-feature correlation
with the target, and a positive control — the same features vs the UN-centred residual's unit mean (between-unit),
to show the pipeline can detect signal where some exists."""
import sys, os, json, numpy as np
sys.path.insert(0, 'analysis')
from E_power import residuals
from E_precheck import label_times, unit_features, CELLF, MMF, N_CENTRE
out = {}
for ls in ['primary', 'strict']:
    F, Y, R, U = [], [], [], []
    for k in range(4):
        for u in residuals(f'runs/chf_{ls}_k{k}'):
            if len(u['y']) <= N_CENTRE: continue
            r = u['y'] - u['p']; ts = label_times(u['car'], u['km'], u['y'])
            rows, _ = unit_features(u['car'], u['km'][N_CENTRE:], ts[N_CENTRE:])
            F += [[f[c] for c in CELLF + MMF] for f in rows]
            Y += list(r[N_CENTRE:] - r[:N_CENTRE].mean()); R += list(r[N_CENTRE:]); U += [u['car']] * len(rows)
    F, Y, R, U = np.array(F, float), np.array(Y), np.array(R), np.array(U)
    F = np.where(np.isnan(F), np.nanmedian(F, 0), F)
    X = np.c_[np.ones(len(F)), (F - F.mean(0)) / (F.std(0) + 1e-9)]
    def r2(Xs, y):
        b, *_ = np.linalg.lstsq(Xs, y, rcond=None); return 1 - ((y - Xs @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    nc = 1 + len(CELLF)
    # positive control: unit-mean features vs unit-mean raw residual (between-unit signal)
    us = np.unique(U); Fm = np.array([F[U == x].mean(0) for x in us]); Rm = np.array([R[U == x].mean() for x in us])
    Xm = np.c_[np.ones(len(us)), (Fm - Fm.mean(0)) / (Fm.std(0) + 1e-9)]
    out[ls] = {'in_sample_r2_percell': float(r2(X[:, :nc], Y)), 'in_sample_r2_all8': float(r2(X, Y)),
               'corr_with_target': {c: round(float(np.corrcoef(F[:, i], Y)[0, 1]), 3) for i, c in enumerate(CELLF + MMF)},
               'corr_with_raw_residual': {c: round(float(np.corrcoef(F[:, i], R)[0, 1]), 3) for i, c in enumerate(CELLF + MMF)},
               'between_unit_in_sample_r2_percell': float(r2(Xm[:, :nc], Rm)), 'n_units': int(len(us))}
    print(ls, json.dumps(out[ls], indent=1), flush=True)
json.dump(out, open('results/E/precheck_diag.json', 'w'), indent=1)
