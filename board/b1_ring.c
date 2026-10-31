/* B1 producer (briefs/B1/README.md §4.1): one pinned thread writes 16 B frames (8 B counter-derived payload + 8 B
 * monotonic sequence number) into an anonymous, pre-populated LPDDR ring at a fixed rate, in 1 ms bursts paced by
 * clock_nanosleep(TIMER_ABSTIME). The main thread (pinned to the dumper core) fires the freeze-and-dump triggers
 * (b1_dump.c) while the producer keeps running.
 *
 * This is a CPU thread, not DMA: its CPU cost is an UPPER BOUND on a DMA path.
 *
 * Build: gcc -O2 -pthread -o b1_ring b1_ring.c b1_dump.c
 * Usage: ./b1_ring RATE_MBPS RING_MB DURATION_S PRODUCER_CORE DUMPER_CORE DUMP_DIR OUT.json [T1:N1 T2:N2 ...]
 *        (trigger Ti seconds after the clock starts dumps the last Ni seconds)
 */
#define _GNU_SOURCE
#include "b1_ring.h"

#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define BURST_NS 1000000LL         /* 1 ms bursts (brief) */
#define DROP_LAG_NS 1000000000LL   /* a burst > 1 s behind schedule is a drop event (brief) */
#define STATUS_BURSTS 10000        /* status every 10 s */
#define MAX_STATUS 4096
#define MAX_DROPS 4096

ring_t R;

static struct { double t_s, mbps, depth_s, thread_cpu_s, max_lag_ms_window; uint64_t head, oldest, drops; } st[MAX_STATUS];
static int nst;
static struct { double t_s, lag_ms; uint64_t seq, missed_bursts; } drops[MAX_DROPS];
static uint64_t lag_hist[5];       /* bursts late by > 0.1, 1, 10, 100, 1000 ms */

static int64_t ns_of(const struct timespec *t) { return (int64_t)t->tv_sec * 1000000000LL + t->tv_nsec; }
int64_t now_ns(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return ns_of(&t); }
static double thread_cpu_s(void) { struct timespec t; clock_gettime(CLOCK_THREAD_CPUTIME_ID, &t); return ns_of(&t) * 1e-9; }

void pin(int core) {
    cpu_set_t s; CPU_ZERO(&s); CPU_SET(core, &s);
    if (pthread_setaffinity_np(pthread_self(), sizeof s, &s)) { perror("affinity"); exit(1); }
}

static void *producer(void *arg) {
    (void)arg;
    pin(R.producer_core);
    const uint64_t per = R.frames_per_burst, nf = R.nframes;
    uint64_t seq = 0, k = 0, win_frames = 0, nd = 0;
    double max_lag_win = 0, cpu0 = thread_cpu_s();
    int64_t t0 = R.t0_ns, win_t = t0, end = t0 + (int64_t)(R.duration_s * 1e9);
    while (1) {
        int64_t sched = t0 + (int64_t)k * BURST_NS;
        if (sched >= end) break;
        struct timespec ts = {sched / 1000000000LL, sched % 1000000000LL};
        while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, NULL) == EINTR) {}
        int64_t now = now_ns(), lag = now - sched;
        double lag_ms = lag * 1e-6;
        if (lag_ms > max_lag_win) max_lag_win = lag_ms;
        if (lag_ms > R.max_lag_ms) R.max_lag_ms = lag_ms;
        for (int b = 0; b < 5; b++) if (lag_ms > (double[]){0.1, 1, 10, 100, 1000}[b]) lag_hist[b]++;
        if (lag > DROP_LAG_NS) {   /* drop event: log, resynchronise to the current schedule slot */
            uint64_t missed = (uint64_t)(lag / BURST_NS);
            if (nd < MAX_DROPS) { drops[nd].t_s = (now - t0) * 1e-9; drops[nd].lag_ms = lag_ms; drops[nd].seq = seq;
                                  drops[nd].missed_bursts = missed; }
            nd++;
            __atomic_store_n(&R.drops, nd, __ATOMIC_RELEASE);
            k += missed;
            R.missed_bursts += missed;
        }
        frame_t *f = R.ring;
        for (uint64_t j = 0; j < per; j++, seq++) {
            frame_t *s = &f[seq % nf];
            s->payload = seq * 0x9E3779B97F4A7C15ULL ^ 0xD1B54A32D192ED03ULL;
            s->seq = seq;
        }
        __atomic_store_n(&R.head, seq, __ATOMIC_RELEASE);
        win_frames += per;
        k++;
        if (k % STATUS_BURSTS == 0 && nst < MAX_STATUS) {
            int64_t tn = now_ns();
            uint64_t oldest = seq > nf ? seq - nf : 0;
            st[nst].t_s = (tn - t0) * 1e-9;
            st[nst].mbps = win_frames * 16.0 / ((tn - win_t) * 1e-9) / 1e6;
            st[nst].head = seq; st[nst].oldest = oldest; st[nst].drops = nd;
            st[nst].depth_s = (seq - oldest) * 16.0 / (R.rate_mbps * 1e6);
            st[nst].thread_cpu_s = thread_cpu_s() - cpu0;
            st[nst].max_lag_ms_window = max_lag_win;
            nst++;
            win_t = tn; win_frames = 0; max_lag_win = 0;
        }
    }
    R.frames_total = seq;
    R.producer_cpu_s = thread_cpu_s() - cpu0;
    R.t_end_ns = now_ns();
    __atomic_store_n(&R.done, 1, __ATOMIC_RELEASE);
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 8) { fprintf(stderr, "usage: %s RATE_MBPS RING_MB DURATION_S PCORE DCORE DUMP_DIR OUT.json [T:N ...]\n", argv[0]); return 2; }
    R.rate_mbps = atof(argv[1]);
    R.ring_mb = atol(argv[2]);
    R.duration_s = atof(argv[3]);
    R.producer_core = atoi(argv[4]);
    int dcore = atoi(argv[5]);
    const char *dir = argv[6], *out = argv[7];
    R.frames_per_burst = (uint64_t)(R.rate_mbps * 1e6 * (BURST_NS * 1e-9) / 16.0 + 0.5);
    R.nframes = ((uint64_t)R.ring_mb << 20) / sizeof(frame_t);
    pin(dcore);

    /* ring: anonymous, MAP_POPULATE (census: MAP_HUGETLB unavailable, THP = always); pre-touched before the clock */
    int64_t ta = now_ns();
    R.ring = mmap(NULL, R.nframes * sizeof(frame_t), PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE, -1, 0);
    if (R.ring == MAP_FAILED) { perror("mmap"); return 1; }
    memset(R.ring, 0xff, R.nframes * sizeof(frame_t));
    double alloc_s = (now_ns() - ta) * 1e-9;

    int ntr = argc - 8;
    trigger_t *tr = calloc(ntr > 0 ? ntr : 1, sizeof *tr);
    for (int i = 0; i < ntr; i++) sscanf(argv[8 + i], "%lf:%lf", &tr[i].at_s, &tr[i].window_s);

    R.t0_ns = now_ns() + 100000000LL;  /* clock starts 100 ms from now */
    pthread_t th;
    if (pthread_create(&th, NULL, producer, NULL)) { perror("pthread_create"); return 1; }
    for (int i = 0; i < ntr; i++) {
        int64_t at = R.t0_ns + (int64_t)(tr[i].at_s * 1e9);
        struct timespec ts = {at / 1000000000LL, at % 1000000000LL};
        while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, NULL) == EINTR) {}
        if (__atomic_load_n(&R.done, __ATOMIC_ACQUIRE)) { tr[i].skipped = 1; continue; }
        dump_window(&tr[i], dir);
    }
    pthread_join(th, NULL);

    double wall = (R.t_end_ns - R.t0_ns) * 1e-9;
    FILE *o = fopen(out, "w");
    if (!o) { perror(out); return 1; }
    fprintf(o, "{\"tag\": \"MEASURED (CPU producer: CPU cost is an upper bound on a DMA path)\",\n");
    fprintf(o, " \"rate_mbps_target\": %.3f, \"ring_mb\": %ld, \"ring_frames\": %lu, \"duration_s\": %.1f, "
               "\"frames_per_burst\": %lu, \"producer_core\": %d, \"dumper_core\": %d,\n",
            R.rate_mbps, R.ring_mb, (unsigned long)R.nframes, R.duration_s, (unsigned long)R.frames_per_burst,
            R.producer_core, dcore);
    fprintf(o, " \"mapping\": \"anonymous MAP_PRIVATE|MAP_POPULATE, THP always, no MAP_HUGETLB\", \"alloc_and_pretouch_s\": %.3f,\n", alloc_s);
    fprintf(o, " \"wall_s\": %.3f, \"frames_total\": %lu, \"achieved_mbps\": %.4f, \"achieved_frac\": %.6f,\n", wall,
            (unsigned long)R.frames_total, R.frames_total * 16.0 / wall / 1e6, R.frames_total * 16.0 / wall / 1e6 / R.rate_mbps);
    fprintf(o, " \"drop_events\": %lu, \"missed_bursts\": %lu, \"max_lag_ms\": %.3f, "
               "\"bursts_late_gt_ms\": {\"0.1\": %lu, \"1\": %lu, \"10\": %lu, \"100\": %lu, \"1000\": %lu},\n",
            (unsigned long)R.drops, (unsigned long)R.missed_bursts, R.max_lag_ms, (unsigned long)lag_hist[0],
            (unsigned long)lag_hist[1], (unsigned long)lag_hist[2], (unsigned long)lag_hist[3], (unsigned long)lag_hist[4]);
    fprintf(o, " \"producer_thread_cpu_s\": %.3f, \"producer_thread_cpu_pct\": %.3f,\n", R.producer_cpu_s, 100.0 * R.producer_cpu_s / wall);
    fprintf(o, " \"measured_depth_s_final\": %.3f, \"arithmetic_depth_s\": %.3f,\n",
            (R.frames_total < R.nframes ? R.frames_total : R.nframes) * 16.0 / (R.rate_mbps * 1e6),
            R.nframes * 16.0 / (R.rate_mbps * 1e6));
    fprintf(o, " \"drops\": [");
    for (uint64_t i = 0; i < R.drops && i < MAX_DROPS; i++)
        fprintf(o, "%s{\"t_s\": %.3f, \"lag_ms\": %.3f, \"seq\": %lu, \"missed_bursts\": %lu}", i ? ", " : "",
                drops[i].t_s, drops[i].lag_ms, (unsigned long)drops[i].seq, (unsigned long)drops[i].missed_bursts);
    fprintf(o, "],\n \"dumps\": [");
    for (int i = 0; i < ntr; i++) { if (i) fprintf(o, ", "); dump_json(o, &tr[i]); }
    fprintf(o, "],\n \"status\": [");
    for (int i = 0; i < nst; i++)
        fprintf(o, "%s\n  {\"t_s\": %.2f, \"mbps\": %.4f, \"drops\": %lu, \"head\": %lu, \"oldest\": %lu, \"depth_s\": %.3f, "
                   "\"thread_cpu_s\": %.4f, \"max_lag_ms\": %.3f}", i ? "," : "", st[i].t_s, st[i].mbps,
                (unsigned long)st[i].drops, (unsigned long)st[i].head, (unsigned long)st[i].oldest, st[i].depth_s,
                st[i].thread_cpu_s, st[i].max_lag_ms_window);
    fprintf(o, "]}\n");
    fclose(o);
    munmap(R.ring, R.nframes * sizeof(frame_t));
    printf("b1_ring %.1f MB/s ring %ld MB: achieved %.4f MB/s, drops %lu, max lag %.3f ms, cpu %.2f %%, dumps",
           R.rate_mbps, R.ring_mb, R.frames_total * 16.0 / wall / 1e6, (unsigned long)R.drops, R.max_lag_ms,
           100.0 * R.producer_cpu_s / wall);
    for (int i = 0; i < ntr; i++) printf(" N%.0f:%s", tr[i].window_s, tr[i].skipped ? "skipped" : tr[i].gate_pass ? "PASS" : "FAIL");
    printf("\n");
    return 0;
}
