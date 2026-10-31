/* B1 shared definitions: ring state (b1_ring.c) and freeze-and-dump (b1_dump.c). */
#ifndef B1_RING_H
#define B1_RING_H
#include <stdint.h>
#include <stdio.h>

typedef struct { uint64_t payload, seq; } frame_t;   /* 16 B: 8 B payload + 8 B sequence number */

typedef struct {
    frame_t *ring;
    uint64_t nframes, frames_per_burst, frames_total, drops, missed_bursts;
    uint64_t head;                 /* next sequence number to write; published with release semantics */
    double rate_mbps, duration_s, max_lag_ms, producer_cpu_s;
    long ring_mb;
    int producer_core, done;
    int64_t t0_ns, t_end_ns;
} ring_t;

typedef struct {
    double at_s, window_s;         /* trigger time after clock start; window length dumped */
    int skipped, gate_pass;
    uint64_t head_at_trigger, first_seq, frames_requested, frames_dumped, expected_frames;
    uint64_t mismatched, first_mismatch_index, drops_before, drops_after;
    double t_snapshot_ms, t_copy_write_s, t_fsync_s, t_total_s, mb, copy_mbps;
    const char *fail_reason;
    char path[512];
} trigger_t;

extern ring_t R;
int64_t now_ns(void);
void pin(int core);
void dump_window(trigger_t *t, const char *dir);
void dump_json(FILE *o, const trigger_t *t);
#endif
