/* Experiment H-b (pre-registered in results/H/H_preregistration.md, commit 43485e8): per-cell charge-limit
 * evaluator at loop rate. Per update: N cell voltages (int16 mV) + P probe temps (int16, 0.1 C) + pack current ->
 * per-cell allowed C-rate = ct_lut[T of the cell's probe] * taper_lut[V] (0 if V >= the cell's own voltage limit),
 * min + argmin over cells, setpoint = min * C_NOM; plus a per-cell EWMA resistance estimate (state only).
 * Build: gcc -O2 -o h_limiter h_limiter.c -lm
 * Usage: ./h_limiter luts.bin frames_N.bin gate_out_N.bin [min_updates=100000] [sustain_s=5]
 * Prints one JSON line. Gate outputs (argmin int32, setpoint float32 per frame, then final R[N] float32) are from a
 * single fresh pass over all frames; latency / sustained-rate loops run afterwards from reset state.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define V0 2500
#define NV 2001
#define T0 (-400)
#define NT 1401
#define C_NOM 120.0f
#ifndef VLIM
#define VLIM 4250
#endif
#define ALPHA 0.05f
#define DI_MIN 5.0f

typedef struct {
    int n, p;
    int16_t *vprev;   /* 2 B / cell */
    float *r;         /* 4 B / cell (mOhm) */
    uint16_t *pidx;   /* 2 B / cell */
    int16_t *vlim;    /* 2 B / cell */
    float iprev;
    int have_prev;
} state_t;

static float taper_lut[NV], ct_lut[NT];

static long kb(const char *key) {
    FILE *f = fopen("/proc/self/status", "r");
    char line[256];
    long v = -1;
    size_t kl = strlen(key);
    while (f && fgets(line, sizeof line, f))
        if (!strncmp(line, key, kl)) { v = atol(line + kl + 1); break; }
    if (f) fclose(f);
    return v;
}

static double now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e9 + ts.tv_nsec;
}

static void reset(state_t *s) {
    for (int k = 0; k < s->n; k++) { s->vprev[k] = 0; s->r[k] = 0.0f; s->pidx[k] = (uint16_t)((long)k * s->p / s->n); s->vlim[k] = VLIM; }
    s->iprev = 0.0f;
    s->have_prev = 0;
}

/* one control update; returns argmin cell, writes setpoint (A) */
static inline int update(state_t *s, const int16_t *v, const int16_t *t, float cur, float *setpoint) {
    float best = 1e30f;
    int arg = 0;
    float di = cur - s->iprev;
    int upd_r = s->have_prev && (di > DI_MIN || di < -DI_MIN);
    for (int k = 0; k < s->n; k++) {
        int vk = v[k];
        int vi = vk - V0; vi = vi < 0 ? 0 : (vi >= NV ? NV - 1 : vi);
        int ti = t[s->pidx[k]] - T0; ti = ti < 0 ? 0 : (ti >= NT ? NT - 1 : ti);
        float c = (vk >= s->vlim[k]) ? 0.0f : ct_lut[ti] * taper_lut[vi];
        if (c < best) { best = c; arg = k; }
        if (upd_r) {
            float rk = (float)(vk - s->vprev[k]) / di;
            s->r[k] += ALPHA * (rk - s->r[k]);
        }
        s->vprev[k] = (int16_t)vk;
    }
    s->iprev = cur;
    s->have_prev = 1;
    *setpoint = best * C_NOM;
    return arg;
}

static int cmpd(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s luts.bin frames.bin gate_out.bin [min_updates] [sustain_s]\n", argv[0]); return 2; }
    long min_upd = argc > 4 ? atol(argv[4]) : 100000;
    double sustain_s = argc > 5 ? atof(argv[5]) : 5.0;
    long rss_start = kb("VmRSS:");

    FILE *f = fopen(argv[2], "rb");
    if (!f) { perror("frames"); return 1; }
    int32_t hdr[3];
    if (fread(hdr, 4, 3, f) != 3) return 1;
    int n = hdr[0], p = hdr[1], nf = hdr[2];
    float *cur = malloc(sizeof(float) * nf);
    int16_t *V = malloc(sizeof(int16_t) * (size_t)nf * n), *T = malloc(sizeof(int16_t) * (size_t)nf * p);
    if (fread(cur, sizeof(float), nf, f) != (size_t)nf || fread(V, 2, (size_t)nf * n, f) != (size_t)nf * n ||
        fread(T, 2, (size_t)nf * p, f) != (size_t)nf * p) { fprintf(stderr, "short frames\n"); return 1; }
    fclose(f);
    long nlat = min_upd;
    double *lat = malloc(sizeof(double) * nlat);
    int32_t *g_arg = malloc(4 * (size_t)nf);
    float *g_sp = malloc(4 * (size_t)nf);
    memset(lat, 0, sizeof(double) * nlat); memset(g_arg, 0, 4 * (size_t)nf); memset(g_sp, 0, 4 * (size_t)nf);
    long rss_before_state = kb("VmRSS:");

    /* limiter state + LUTs (LUTs are static arrays; touch them by loading) */
    state_t s = {.n = n, .p = p};
    s.vprev = malloc(2 * (size_t)n); s.r = malloc(4 * (size_t)n); s.pidx = malloc(2 * (size_t)n); s.vlim = malloc(2 * (size_t)n);
    FILE *fl = fopen(argv[1], "rb");
    if (!fl || fread(taper_lut, 4, NV, fl) != NV || fread(ct_lut, 4, NT, fl) != NT) { fprintf(stderr, "luts\n"); return 1; }
    fclose(fl);
    reset(&s);

    /* gate pass: one fresh pass over every frame */
    for (int i = 0; i < nf; i++) g_arg[i] = update(&s, V + (size_t)i * n, T + (size_t)i * p, cur[i], &g_sp[i]);
    FILE *go = fopen(argv[3], "wb");
    fwrite(g_arg, 4, nf, go); fwrite(g_sp, 4, nf, go); fwrite(s.r, 4, n, go);
    fclose(go);

    /* latency: per-update timing */
    reset(&s);
    volatile float sink = 0; float sp;
    for (long u = 0; u < nlat; u++) {
        int i = (int)(u % nf);
        double t0 = now_ns();
        int a = update(&s, V + (size_t)i * n, T + (size_t)i * p, cur[i], &sp);
        double t1 = now_ns();
        lat[u] = t1 - t0;
        sink += sp + a;
    }
    /* sustained rate: tight loop, clock checked every 1024 updates */
    reset(&s);
    long cnt = 0;
    double ts0 = now_ns(), tend = ts0 + sustain_s * 1e9, tnow = ts0;
    while (tnow < tend) {
        for (int j = 0; j < 1024; j++, cnt++) {
            int i = (int)(cnt % nf);
            sink += update(&s, V + (size_t)i * n, T + (size_t)i * p, cur[i], &sp);
        }
        tnow = now_ns();
    }
    double rate = cnt / ((tnow - ts0) * 1e-9);
    long hwm = kb("VmHWM:"), rss_end = kb("VmRSS:");
    double lsum = 0; for (long u = 0; u < nlat; u++) lsum += lat[u];
    qsort(lat, nlat, sizeof(double), cmpd);
    size_t state_b = (size_t)n * (2 + 4 + 2 + 2) + sizeof(float) + sizeof(int);
    size_t lut_b = sizeof taper_lut + sizeof ct_lut;
    size_t frame_b = (size_t)nf * (n * 2 + p * 2 + 4);
    printf("{\"n\": %d, \"p\": %d, \"frames\": %d, \"updates_timed\": %ld, \"lat_ns_p50\": %.0f, \"lat_ns_p99\": %.0f, "
           "\"lat_ns_max\": %.0f, \"lat_ns_mean\": %.1f, \"sustained_updates_per_s\": %.0f, \"state_bytes\": %zu, "
           "\"state_bytes_per_cell\": 10, \"lut_bytes\": %zu, \"frame_buffer_bytes\": %zu, \"rss_start_kb\": %ld, "
           "\"rss_before_state_kb\": %ld, \"rss_end_kb\": %ld, \"hwm_kb\": %ld, \"sink\": %.1f}\n",
           n, p, nf, nlat, lat[nlat / 2], lat[(long)(nlat * 0.99)], lat[nlat - 1],
           lsum / nlat, rate, state_b, lut_b, frame_b, rss_start, rss_before_state, rss_end, hwm, (double)(sink > 0));
    return 0;
}
