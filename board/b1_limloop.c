/* B1 concurrent real-time load, core 2 (briefs/B1/README.md §4.2): the H-b limiter at 100 Hz, alternating the 96-cell
 * (NMC map, VLIM 4250 mV) and 3,564-cell (H2 LFP map, VLIM 3650 mV) inputs per 60 s block, p50/p99 per block, gate per
 * block. The limiter itself is h_limiter.c, included unchanged (its main() renamed); only the loop is new.
 *
 * Gate per block: a fresh pass over every frame, compared byte for byte with a gate_out file that passed the host
 * C<->Python gate (h_ref.py / h2_ref.py gate) in the same session's census.
 * Build: gcc -O2 -o b1_limloop b1_limloop.c -lm
 * Usage: ./b1_limloop DURATION_S OUT.jsonl  luts96 frames96 ref96  luts3564 frames3564 ref3564
 */
#define main hl_main
#include "h_limiter.c"
#undef main
#include <errno.h>
#include <signal.h>

#define TICK_NS 10000000LL   /* 100 Hz */
#ifndef BLOCK_S
#define BLOCK_S 60
#endif

typedef struct {
    int n, p, nf, vlim;
    float *cur, lut_t[NV], lut_c[NT];
    int16_t *V, *T;
    char *ref; size_t ref_bytes;
    state_t s;
} cfg_t;

static volatile sig_atomic_t stop;
static void on_sig(int x) { (void)x; stop = 1; }

static void *slurp(const char *p, size_t *len) {
    FILE *f = fopen(p, "rb");
    if (!f) { perror(p); exit(1); }
    fseek(f, 0, SEEK_END); *len = ftell(f); fseek(f, 0, SEEK_SET);
    void *b = malloc(*len);
    if (fread(b, 1, *len, f) != *len) { fprintf(stderr, "short %s\n", p); exit(1); }
    fclose(f);
    return b;
}

static void load(cfg_t *c, const char *luts, const char *frames, const char *ref, int vlim) {
    FILE *f = fopen(frames, "rb");
    int32_t hdr[3];
    if (!f || fread(hdr, 4, 3, f) != 3) { perror(frames); exit(1); }
    c->n = hdr[0]; c->p = hdr[1]; c->nf = hdr[2]; c->vlim = vlim;
    c->cur = malloc(4 * (size_t)c->nf);
    c->V = malloc(2 * (size_t)c->nf * c->n); c->T = malloc(2 * (size_t)c->nf * c->p);
    if (fread(c->cur, 4, c->nf, f) != (size_t)c->nf || fread(c->V, 2, (size_t)c->nf * c->n, f) != (size_t)c->nf * c->n ||
        fread(c->T, 2, (size_t)c->nf * c->p, f) != (size_t)c->nf * c->p) { fprintf(stderr, "short frames\n"); exit(1); }
    fclose(f);
    FILE *fl = fopen(luts, "rb");
    if (!fl || fread(c->lut_t, 4, NV, fl) != NV || fread(c->lut_c, 4, NT, fl) != NT) { perror(luts); exit(1); }
    fclose(fl);
    c->ref = slurp(ref, &c->ref_bytes);
    c->s.n = c->n; c->s.p = c->p;
    c->s.vprev = malloc(2 * (size_t)c->n); c->s.r = malloc(4 * (size_t)c->n);
    c->s.pidx = malloc(2 * (size_t)c->n); c->s.vlim = malloc(2 * (size_t)c->n);
}

static void use(cfg_t *c) {   /* h_limiter.c keeps its LUTs in file-scope arrays and VLIM in reset() */
    memcpy(taper_lut, c->lut_t, sizeof taper_lut); memcpy(ct_lut, c->lut_c, sizeof ct_lut);
    reset(&c->s);
    for (int k = 0; k < c->n; k++) c->s.vlim[k] = (int16_t)c->vlim;
}

static int gate(cfg_t *c) {
    use(c);
    size_t nb = 8 * (size_t)c->nf + 4 * (size_t)c->n;
    char *g = malloc(nb);
    int32_t *ga = (int32_t *)g; float *gs = (float *)(g + 4 * (size_t)c->nf);
    for (int i = 0; i < c->nf; i++) ga[i] = update(&c->s, c->V + (size_t)i * c->n, c->T + (size_t)i * c->p, c->cur[i], &gs[i]);
    memcpy(g + 8 * (size_t)c->nf, c->s.r, 4 * (size_t)c->n);
    int ok = nb == c->ref_bytes && !memcmp(g, c->ref, nb);
    free(g);
    return ok;
}

int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage: %s DURATION_S OUT.jsonl luts96 frames96 ref96 luts3564 frames3564 ref3564\n", argv[0]); return 2; }
    double dur = atof(argv[1]);
    FILE *o = fopen(argv[2], "w");
    if (!o) { perror(argv[2]); return 1; }
    static cfg_t cf[2];
    load(&cf[0], argv[3], argv[4], argv[5], 4250);
    load(&cf[1], argv[6], argv[7], argv[8], 3650);
    signal(SIGTERM, on_sig); signal(SIGINT, on_sig);
    long per_block = BLOCK_S * 1000000000LL / TICK_NS;
    double *lat = malloc(sizeof(double) * per_block);
    double t_start = now_ns(), t_end = t_start + dur * 1e9;
    volatile float sink = 0;
    for (int b = 0; !stop && now_ns() < t_end; b++) {
        cfg_t *c = &cf[b % 2];
        double wall0 = (double)time(NULL);
        int g = gate(c);
        use(c);
        long u = 0, late = 0;
        double max_late = 0, blk0 = now_ns();
        long long next = (long long)blk0 + TICK_NS;
        for (; u < per_block && !stop && next < t_end; u++) {
            struct timespec ts = {next / 1000000000LL, next % 1000000000LL};
            while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, NULL) == EINTR && !stop) {}
            double tw = now_ns(), lt = (tw - next) * 1e-3;
            if (lt > max_late) max_late = lt;
            if (lt > 1000) late++;
            int i = (int)(u % c->nf);
            float sp;
            double t0 = now_ns();
            int a = update(&c->s, c->V + (size_t)i * c->n, c->T + (size_t)i * c->p, c->cur[i], &sp);
            lat[u] = now_ns() - t0;
            sink += sp + a;
            next += TICK_NS;
        }
        if (!u) break;
        double lsum = 0; for (long k = 0; k < u; k++) lsum += lat[k];
        qsort(lat, u, sizeof(double), cmpd);
        fprintf(o, "{\"block\": %d, \"wall_start\": %.0f, \"t_s\": %.1f, \"n_cells\": %d, \"gate_pass\": %s, \"updates\": %ld, "
                   "\"lat_ns_p50\": %.0f, \"lat_ns_p99\": %.0f, \"lat_ns_p999\": %.0f, \"lat_ns_max\": %.0f, \"lat_ns_mean\": %.1f, "
                   "\"tick_late_max_us\": %.1f, \"ticks_late_gt_1ms\": %ld, \"partial\": %s}\n",
                b, wall0, (blk0 - t_start) * 1e-9, c->n, g ? "true" : "false", u, lat[u / 2], lat[(long)(u * 0.99)],
                lat[(long)(u * 0.999)], lat[u - 1], lsum / u, max_late, late, u < per_block ? "true" : "false");
        fflush(o);
    }
    fclose(o);
    return sink < -1 ? 1 : 0;
}
