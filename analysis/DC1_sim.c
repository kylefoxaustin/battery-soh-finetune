/* DC1 plant loop and causal forecasters (results/DC1/DC1_preregistration.md §2, §4.2, §4.3, D-2).
 *
 * Called from analysis/DC1_storage.py through ctypes. DC1_storage.py holds a pure-Python reference for every function
 * here and gates them against each other (§4.5) before any E* is reported.
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

static double clip(double x, double lo, double hi) { return x < lo ? lo : (x > hi ? hi : x); }

/* §2 common step, driven by the §4.1/§4.2 reference. dhat[t] is the forecast step (0 for K0).
 * Returns the number of violating frames; soe_out / pup_out may be NULL. */
int dc1_sim(const double *P, const double *dhat, int N, double E, double s_tgt, double T_rec, double g, double R,
            double Pmax, double Pmax_s, double dt, double eta_c, double eta_d, double *soe_out, double *pup_out)
{
    double lim = R * Pmax * dt, tol = 1e-9 * Pmax, k = g / (2.0 * R * Pmax * E);
    double soe = s_tgt * E, pup_prev = P[0];
    int viol = 0;
    if (soe_out) soe_out[0] = soe;
    if (pup_out) pup_out[0] = pup_prev;
    for (int t = 1; t < N; t++) {
        double d = dhat[t], s = s_tgt;
        if (g != 0.0) s = clip(s_tgt + k * (d > 0 ? 1.0 : (d < 0 ? -1.0 : 0.0)) * d * d, 0.05, 0.95);
        double r = P[t] + (s * E - soe) / T_rec;
        double pst = clip(r, pup_prev - lim, pup_prev + lim);
        double lo = fmax(-Pmax_s, -(E - soe) / (eta_c * dt));
        double hi = fmin(Pmax_s, soe * eta_d / dt);
        double ps = clip(P[t] - pst, lo, hi);
        double pup = P[t] - ps;
        if (ps > 0) soe -= ps * dt / eta_d; else soe -= ps * dt * eta_c;
        if (fabs(pup - pup_prev) > lim + tol) viol++;
        pup_prev = pup;
        if (soe_out) soe_out[t] = soe;
        if (pup_out) pup_out[t] = pup;
    }
    return viol;
}

/* Pearson correlation of a[0..n) with b[0..n); NAN if either has zero variance. */
static double pearson(const double *a, const double *b, int n)
{
    double ma = 0, mb = 0;
    for (int i = 0; i < n; i++) { ma += a[i]; mb += b[i]; }
    ma /= n; mb /= n;
    double sab = 0, saa = 0, sbb = 0;
    for (int i = 0; i < n; i++) {
        double x = a[i] - ma, y = b[i] - mb;
        sab += x * y; saa += x * x; sbb += y * y;
    }
    if (saa <= 0 || sbb <= 0) return NAN;
    return sab / sqrt(saa * sbb);
}

/* §4.2 steps 1-3 (K1) and §4.3 (K1-sh when perm != NULL). Frames t < nW-1 have no full window: persistence (dhat 0).
 * perm holds one permutation of 0..nW-1 per frame t >= nW-1, row (t - nW + 1). Lstar_out[t] = L* or 0 (persistence). */
void dc1_fc_seasonal(const double *P, int N, int nW, int Lmin, int Hp, double rho_min, const int32_t *perm,
                     double *dhat, int32_t *Lstar_out)
{
    double *w = malloc(sizeof(double) * (nW > 0 ? nW : 1));
    int Lmax = nW / 2;
    for (int t = 0; t < N; t++) {
        dhat[t] = 0.0;
        Lstar_out[t] = 0;
        if (t < nW - 1 || Lmax < Lmin) continue;
        const double *src = P + t - nW + 1;
        if (perm) {
            const int32_t *pr = perm + (size_t)(t - nW + 1) * nW;
            for (int i = 0; i < nW; i++) w[i] = src[pr[i]];
        } else {
            for (int i = 0; i < nW; i++) w[i] = src[i];
        }
        double best = -2.0;
        int L = 0;
        for (int l = Lmin; l <= Lmax; l++) {
            double r = pearson(w + l, w, nW - l);
            if (!isnan(r) && r > best) { best = r; L = l; }
        }
        if (L == 0 || best < rho_min) continue;
        Lstar_out[t] = L;
        double dm = 0.0;
        for (int h = 1; h <= Hp; h++) {
            int kk = (h + L - 1) / L;
            double d = w[nW - 1 + h - kk * L] - P[t];
            if (fabs(d) > fabs(dm)) dm = d;
        }
        dhat[t] = dm;
    }
    free(w);
}

/* D-2 K1-r (perm == NULL) and K1-r-sh: least-squares slope of the last n samples against time positions 0..n-1,
 * extrapolated from P[t]; frames t < n-1 have no full window (dhat 0). perm rows as in dc1_fc_seasonal. */
void dc1_fc_ramp(const double *P, int N, int n, int Hp, const int32_t *perm, double *dhat)
{
    double xm = (n - 1) / 2.0, sxx = 0;
    for (int i = 0; i < n; i++) sxx += (i - xm) * (i - xm);
    for (int t = 0; t < N; t++) {
        dhat[t] = 0.0;
        if (t < n - 1) continue;
        const double *src = P + t - n + 1;
        const int32_t *pr = perm ? perm + (size_t)(t - n + 1) * n : NULL;
        double vm = 0;
        for (int i = 0; i < n; i++) vm += pr ? src[pr[i]] : src[i];
        vm /= n;
        double sxy = 0;
        for (int i = 0; i < n; i++) sxy += (i - xm) * ((pr ? src[pr[i]] : src[i]) - vm);
        double b = sxy / sxx, dm = 0.0;
        for (int h = 1; h <= Hp; h++) {
            double d = b * h;
            if (fabs(d) > fabs(dm)) dm = d;
        }
        dhat[t] = dm;
    }
}
