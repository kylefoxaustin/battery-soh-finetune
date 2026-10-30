"""DERIVED arithmetic for the ANGLES report. All inputs stated inline and tagged."""
GB = 1e9

# --- 1. Rolling-window depth by medium (DERIVED; rates from brief §2.2) -------------
rates = {'10% farmed (3.2 MB/s)': 3.2e6, '100% farmed (32 MB/s)': 32e6, 'ADC ceiling (60 MB/s)': 60e6,
         'per-GPU phases, brief §7 (12 MB/s)': 12e6, '8-GPU board, brief §7 (100 MB/s)': 100e6}
media = {'MCU on-chip SRAM 3 MB': 3e6, 'HyperRAM 128 MB window (max)': 128e6,
         'MCU + SDRAM 64 MB (crossover-MCU class, 512 Mb)': 64e6, 'MCU + SDRAM 256 MB (32-bit, 2 Gb)': 256e6,
         'LPDDR 2 GB': 2e9, 'LPDDR 8 GB': 8e9}
print("Rolling raw window (seconds) = capacity / rate")
print(f"{'medium':45s}" + "".join(f"{k:>38s}" for k in rates))
for m, cap in media.items():
    print(f"{m:45s}" + "".join(f"{cap/r:38.1f}" for r in rates.values()))

# --- 2. Flash as the rolling medium: time to exhaust endurance (DERIVED; endurance ASSUMED) ---
print("\nFlash exhaustion if used as a continuous ring buffer (TBW = capacity x P/E cycles; write amplification 1.0 ASSUMED)")
for cap_gb, pe, label in ((64, 3000, 'eMMC MLC-class 64 GB, 3k P/E (ASSUMED)'),
                          (256, 3000, 'eMMC MLC-class 256 GB, 3k P/E (ASSUMED)'),
                          (256, 1000, 'eMMC TLC-class 256 GB, 1k P/E (ASSUMED)')):
    tbw = cap_gb * GB * pe
    row = [f"{tbw / r / 86400 / 365:.1f} y" for r in rates.values()]
    print(f"{label:45s}" + "".join(f"{x:>38s}" for x in row))
print("15-year vehicle life at 3.2 MB/s needs TBW =", f"{3.2e6*86400*365*15/1e15:.2f} PB")

# --- 3. Re-read factor (DERIVED): bandwidth needed to re-scan a resident window N times per window period ---
print("\nRe-read bandwidth: window ingested at R, scanned k times -> k*R; share of medium bandwidth")
for k in (1, 10, 100):
    for R, lbl in ((3.2e6, '3.2 MB/s'), (32e6, '32 MB/s')):
        need = k * R
        print(f"k={k:>3} at {lbl}: {need/1e6:8.0f} MB/s  = HyperRAM {100*need/0.4e9:6.1f} %   SDRAM-200/32b {100*need/0.8e9:6.1f} %   LPDDR5 measured read {100*need/12.0e9:6.2f} %")

# --- 4. Data-centre provisioned-power margin (DERIVED from SOURCED) ----------------
capex_per_mw = 11.3e6            # SOURCED: JLL 2026 shell-and-core global average
power_share = (0.40, 0.50)       # SOURCED: electrical infrastructure share of build cost
rack_kw = 130                    # ASSUMED: GB200 NVL72-class rack
for share in power_share:
    usd_per_w = capex_per_mw * share / 1e6
    print(f"\npower-infra capex ~ ${usd_per_w:.2f}/W (share {share:.0%})")
    for oversub in (0.10, 0.20, 0.25):
        print(f"  oversubscription {oversub:.0%}: per {rack_kw} kW rack = ${oversub*rack_kw*1e3*usd_per_w/1e3:,.0f}k;"
              f"  per 100 MW site = ${oversub*100e6*usd_per_w/1e6:,.0f}M")

# --- 5. EV reserve analogue scale (from lifecost, SOURCED in-repo) -----------------
print("\nEV: lifecost C2A 20%->5% = $1,700 p50 per vehicle; C1 $58/K; C3 $148 (all ASSUMED-input Monte Carlo)")

# --- 6. Real-option / requirement-volatility arithmetic (DERIVED; inputs ASSUMED) ---
print("\nRequirement-volatility option value per vehicle = P(event) x re-spin cost / volume, summed over platform life")
for respin in (10e6, 30e6):
    for volume in (200e3, 1e6):
        for n_events in (1, 2, 3):
            print(f"  re-spin ${respin/1e6:.0f}M, volume {volume/1e3:.0f}k, {n_events} events: ${n_events*respin/volume:,.0f}/vehicle")
