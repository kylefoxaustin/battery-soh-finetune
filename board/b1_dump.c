/* B1 freeze-and-dump (briefs/B1/README.md §4.3). On a trigger: snapshot the ring head, copy the last N seconds
 * (oldest first) to a new file on the dump partition, fsync, and verify in the same run that the sequence numbers
 * written are contiguous and their count equals N x rate / 16 within one burst. The producer KEEPS RUNNING during the
 * dump, so a slow copy lets the producer overwrite the oldest part of the window: that is reported as GATE FAIL with
 * the overwrite depth, never adjusted.
 *
 * Verification is on the bytes handed to write(): each 4 MB chunk is copied from the ring to a staging buffer, checked,
 * then written from that same buffer. The file is deleted after the gate (brief §6: no dump files left behind).
 */
#define _GNU_SOURCE
#include "b1_ring.h"

#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CHUNK_FRAMES ((4u << 20) / sizeof(frame_t))

void dump_window(trigger_t *t, const char *dir) {
    static frame_t *buf;
    if (!buf && posix_memalign((void **)&buf, 4096, CHUNK_FRAMES * sizeof(frame_t))) { perror("memalign"); exit(1); }
    int64_t t0 = now_ns();
    uint64_t h = __atomic_load_n(&R.head, __ATOMIC_ACQUIRE);
    t->drops_before = __atomic_load_n(&R.drops, __ATOMIC_ACQUIRE);
    t->head_at_trigger = h;
    t->expected_frames = (uint64_t)(t->window_s * R.rate_mbps * 1e6 / 16.0 + 0.5);
    uint64_t want = t->expected_frames, avail = h < R.nframes ? h : R.nframes;
    t->frames_requested = want;
    t->fail_reason = NULL;
    if (want > avail) { want = avail; t->fail_reason = "window exceeds the ring's live span"; }
    uint64_t first = h - want;
    t->first_seq = first;
    t->t_snapshot_ms = (now_ns() - t0) * 1e-6;
    snprintf(t->path, sizeof t->path, "%s/b1_dump_%.0fMBps_%ldMB_N%.0f_%ld.bin", dir, R.rate_mbps, R.ring_mb,
             t->window_s, (long)getpid());
    int fd = open(t->path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { perror(t->path); exit(1); }
    uint64_t done = 0, mism = 0, first_bad = UINT64_MAX;
    while (done < want) {
        uint64_t n = want - done < CHUNK_FRAMES ? want - done : CHUNK_FRAMES;
        uint64_t s0 = first + done, i0 = s0 % R.nframes, part = R.nframes - i0 < n ? R.nframes - i0 : n;
        memcpy(buf, R.ring + i0, part * sizeof(frame_t));
        if (part < n) memcpy(buf + part, R.ring, (n - part) * sizeof(frame_t));
        for (uint64_t j = 0; j < n; j++)
            if (buf[j].seq != s0 + j) { mism++; if (first_bad == UINT64_MAX) first_bad = done + j; }
        size_t bytes = n * sizeof(frame_t), off = 0;
        while (off < bytes) {
            ssize_t w = write(fd, (char *)buf + off, bytes - off);
            if (w < 0) { perror("write"); exit(1); }
            off += (size_t)w;
        }
        done += n;
    }
    int64_t t1 = now_ns();
    if (fsync(fd)) { perror("fsync"); exit(1); }
    close(fd);
    int64_t t2 = now_ns();
    off_t sz = 0;
    { int rfd = open(t->path, O_RDONLY); if (rfd >= 0) { sz = lseek(rfd, 0, SEEK_END); close(rfd); } }
    unlink(t->path);
    t->frames_dumped = (uint64_t)sz / sizeof(frame_t);
    t->mismatched = mism;
    t->first_mismatch_index = first_bad == UINT64_MAX ? 0 : first_bad;
    t->drops_after = __atomic_load_n(&R.drops, __ATOMIC_ACQUIRE);
    t->t_copy_write_s = (t1 - t0) * 1e-9;
    t->t_fsync_s = (t2 - t1) * 1e-9;
    t->t_total_s = (t2 - t0) * 1e-9;
    t->mb = sz / 1e6;
    t->copy_mbps = t->mb / t->t_total_s;
    int64_t slack = (int64_t)t->frames_dumped - (int64_t)t->expected_frames;
    if (!t->fail_reason && mism) t->fail_reason = "producer overwrote part of the window during the copy";
    if (!t->fail_reason && (slack > (int64_t)R.frames_per_burst || -slack > (int64_t)R.frames_per_burst))
        t->fail_reason = "dumped count differs from N x rate / 16 by more than one burst";
    t->gate_pass = t->fail_reason == NULL;
}

void dump_json(FILE *o, const trigger_t *t) {
    if (t->skipped) { fprintf(o, "{\"at_s\": %.1f, \"window_s\": %.0f, \"skipped\": true}", t->at_s, t->window_s); return; }
    fprintf(o, "{\"at_s\": %.1f, \"window_s\": %.0f, \"gate\": \"%s\", \"fail_reason\": %s%s%s, \"head_at_trigger\": %lu, "
               "\"first_seq\": %lu, \"expected_frames\": %lu, \"frames_dumped\": %lu, \"mismatched_frames\": %lu, "
               "\"overwrite_depth_s\": %.3f, \"first_mismatch_index\": %lu, \"mb\": %.3f, \"snapshot_ms\": %.3f, "
               "\"copy_write_s\": %.3f, \"fsync_s\": %.3f, \"total_s\": %.3f, \"copy_mbps\": %.2f, "
               "\"producer_drops_during_dump\": %lu}",
            t->at_s, t->window_s, t->gate_pass ? "PASS" : "FAIL", t->fail_reason ? "\"" : "",
            t->fail_reason ? t->fail_reason : "null", t->fail_reason ? "\"" : "", (unsigned long)t->head_at_trigger,
            (unsigned long)t->first_seq, (unsigned long)t->expected_frames, (unsigned long)t->frames_dumped,
            (unsigned long)t->mismatched, t->mismatched * 16.0 / (R.rate_mbps * 1e6), (unsigned long)t->first_mismatch_index,
            t->mb, t->t_snapshot_ms, t->t_copy_write_s, t->t_fsync_s, t->t_total_s, t->copy_mbps,
            (unsigned long)(t->drops_after - t->drops_before));
}
