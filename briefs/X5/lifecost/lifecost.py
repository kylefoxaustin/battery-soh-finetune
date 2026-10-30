"""Lifetime battery cost model: are three public-domain-style claims consistent?

  C1  "1 C cooler charging is worth ~$100 per vehicle"
  C2  "a reserve can shrink from 20 % to 5 % with the same customer benefit"
  C3  "combining charge and discharge control on one processor removes two ECUs"

Every input is ASSUMED and swept. Regulatory figures are quoted from memory
(UN GTR 22 / Euro 7 durability floors) and must be verified before citing.
Monte Carlo over the assumption ranges; seed 0; results are DERIVED.
"""
import numpy as np, json

rng = np.random.default_rng(0)
N = 200_000
R = 8.314

def U(a, b, n=N): return rng.uniform(a, b, n)

# =====================================================================
# Shared pack economics (ASSUMED)
# =====================================================================
E_USABLE   = 75.0            # kWh the customer can use (fixed in every case)
PACK_COST  = U(90, 140)      # $/kWh, pack level

# =====================================================================
# C1 — degradation channel: cooler charging -> slower fade -> fewer cells
# =====================================================================
# Arrhenius sensitivity of the fade attributable to time spent hot while
# charging. dF/dT = F * s * Ea / (R T^2), T = charge temperature.
EA      = U(30e3, 65e3)      # J/mol, SEI-growth activation energy (literature 30-65)
T_CHG   = U(35, 55) + 273.15 # K, cell temperature while fast-charging hot
F_LIFE  = U(0.12, 0.30)      # total fade over the durability window
S_CHG   = U(0.15, 0.60)      # share of that fade driven by charging-time heat
dF_dT   = F_LIFE * S_CHG * EA / (R * T_CHG**2)          # fraction per kelvin

# Only pays if durability (not range) sizes the pack: gross = U_floor / (1 - F)
# Marginal saving of 1 K: gross * dF / (1 - F)
GROSS_DUR = E_USABLE / (1 - F_LIFE)
save_C1_sizing = PACK_COST * GROSS_DUR * dF_dT / (1 - F_LIFE)

# Second channel that pays even when range sizes the pack: expected warranty
# cost. P(claim) rises with fade; cost per claim ~ module/pack replacement.
P_CLAIM   = U(0.005, 0.03)   # base probability of a capacity warranty claim
CLAIM_USD = U(3000, 9000)    # cost per claim
ELAST     = U(4, 10)         # d ln P(claim) / d F  (claims rise steeply with fade)
save_C1_warranty = P_CLAIM * CLAIM_USD * ELAST * dF_dT

# =====================================================================
# C2 — reserve channel, two possible meanings
# =====================================================================
# (A) an UNCERTAINTY reserve below displayed 0 %: sized to cover the error in
#     knowing the weakest cell's remaining energy. Shrinking it means
#     usable = gross * (1 - r) needs fewer cells.
def gross_for(r): return E_USABLE / (1 - r)
dA_kwh = gross_for(0.20) - gross_for(0.05)
save_C2A = PACK_COST * dA_kwh
# what a smaller, more realistic improvement buys
dA_kwh_half = gross_for(0.20) - gross_for(0.10)
save_C2A_half = PACK_COST * dA_kwh_half
# required precision gain if r = z * sigma with z fixed
precision_gain_needed = 0.20 / 0.05

# (B) a DURABILITY reserve: hidden energy released over life so reported
#     energy stays above a floor (GTR 22 / Euro 7: 80 % at 5 y / 100,000 km,
#     70-72 % at 8 y / 160,000 km — FROM MEMORY, verify).
#     Cutting it from 20 % to 5 % means life-fade must fall from ~20 % to ~5 %.
fade_ratio_needed_B = 0.20 / 0.05
# Temperature drop that would deliver a 4x fade cut on the heat-driven share:
#   F' = F (1 - s + s * exp(-Ea/R (1/(T-dT) - 1/T)))
def fade_after_cooling(dT):
    return F_LIFE * (1 - S_CHG + S_CHG*np.exp(-EA/R*(1/(T_CHG-dT) - 1/T_CHG)))
reachable_B = np.mean(fade_after_cooling(15.0) <= 0.25*F_LIFE)

# =====================================================================
# C3 — removing two ECUs (ASSUMED per-ECU costs, $ per vehicle)
# =====================================================================
def ecu():
    silicon   = U(8, 22)     # MCU, PMIC, transceivers
    pcb       = U(5, 12)     # board + passives
    housing   = U(6, 15)     # enclosure + connector
    assembly  = U(3, 8)      # SMT, test, EOL
    harness   = U(10, 30)    # connector pair, wires, routing labour
    eng       = U(5, 20)     # validation + software amortised per vehicle
    mass_kg   = U(0.4, 1.2)  # ECU + its harness share
    return silicon+pcb+housing+assembly+harness+eng, mass_kg
c1, m1 = ecu(); c2, m2 = ecu()
# mass -> battery-equivalent: d(energy)/d(mass) ~ 0.6 x mass fraction (ASSUMED)
VEH_KG = 1900.0
mass_value = (m1+m2)/VEH_KG * 0.6 * E_USABLE * PACK_COST
save_C3 = c1 + c2 + mass_value

def q(x): return {f'p{p}': round(float(np.percentile(x, p)), 1) for p in (10, 50, 90)}

if __name__ == '__main__':
    res = {
      'C1_degradation_sizing_usd_per_K':   q(save_C1_sizing),
      'C1_warranty_usd_per_K':             q(save_C1_warranty),
      'C1_total_usd_per_K':                q(save_C1_sizing + save_C1_warranty),
      'C1_share_in_50_to_200':  round(float(np.mean((save_C1_sizing+save_C1_warranty>=50)&(save_C1_sizing+save_C1_warranty<=200))),3),
      'C1_fade_saved_pct_capacity_per_K':  q(100*dF_dT),
      'C2A_uncertainty_reserve_20to5_usd': q(save_C2A),
      'C2A_kwh_saved_20to5':               round(float(dA_kwh), 2),
      'C2A_uncertainty_reserve_20to10_usd':q(save_C2A_half),
      'C2A_precision_gain_needed_x':       precision_gain_needed,
      'C2B_durability_reserve_fade_cut_needed_x': fade_ratio_needed_B,
      'C2B_share_reachable_with_15K_cooler': round(float(reachable_B),3),
      'C3_two_ecus_usd':                   q(save_C3),
      'C3_mass_value_usd':                 q(mass_value),
    }
    json.dump(res, open('results.json','w'), indent=1)
    for k,v in res.items(): print(f'{k:42s} {v}')
