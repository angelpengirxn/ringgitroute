"""
Independent verification of the RinggitRoute scenario results
==============================================================

Purpose (brief, section 4: "Check AI-generated answers against independently verified
calculations"): every number shown in the app, report, slides and poster is recomputed
here WITHOUT using the app's engine formulas. This script:

  * re-types the scenario inputs by hand (it does not read them from the engine),
  * uses Python's Decimal type at 28-digit precision instead of floating point,
  * computes multi-period growth through exp(T x ln(1 + rate)) rather than ** powers,
  * computes the money-market hedge step by step, as a student would on paper,

and then compares each result with the engine's output. Any difference larger than
1e-9 (relative) is reported as a FAIL.

Run:  python verification/independent_check.py
Output: evidence/verification_table.csv and evidence/verification_report.md
"""
from __future__ import annotations

import csv
import os
import sys
from decimal import Decimal as D, getcontext

getcontext().prec = 28
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from engine.fx_engine import evaluate          # noqa: E402  (used ONLY for comparison)
from engine.scenarios import PRESETS           # noqa: E402


def g(rate: D, years: D) -> D:
    """(1+rate)^years via exp(years * ln(1+rate)) in Decimal."""
    return (years * (D(1) + rate).ln()).exp()


# Inputs typed independently from the scenario sheet in the report (Table 6.1)
HAND_INPUTS = {
    "A. UK Master's - baseline": dict(S=D("5.5000"), q=D(1), m=D(12), ih=D("0.03"), if_=D("0.04"),
                                      ph=D("0.02"), pf=D("0.03"), fixed=D("14000"), var=D("8000")),
    "B. UK Master's - Malaysian inflation shock": dict(S=D("5.5000"), q=D(1), m=D(12), ih=None, if_=D("0.04"),
                                                       ph=D("0.05"), pf=D("0.03"), fixed=D("14000"), var=D("8000")),
    "C. Japan exchange semester - 6 months": dict(S=D("2.9000"), q=D(100), m=D(6), ih=D("0.03"), if_=D("0.0075"),
                                                  ph=D("0.02"), pf=D("0.025"), fixed=D("300000"), var=D("900000")),
}
# Scenario B: Malaysian real rate from scenario A held constant (Fisher), new inflation 5%
_rA = (D(1) + D("0.03")) / (D(1) + D("0.02")) - D(1)
HAND_INPUTS["B. UK Master's - Malaysian inflation shock"]["ih"] = (D(1) + _rA) * (D(1) + D("0.05")) - D(1)


def hand_calc(x: dict) -> dict:
    T = x["m"] / D(12)
    real_h = (D(1) + x["ih"]) / (D(1) + x["ph"]) - D(1)
    real_f = (D(1) + x["if_"]) / (D(1) + x["pf"]) - D(1)
    F = x["S"] * g(x["ih"], T) / g(x["if_"], T)
    ppp = x["S"] * g(x["ph"], T) / g(x["pf"], T)
    var_T = x["var"] * g(x["pf"], T)
    total_fc = x["fixed"] + var_T
    fwd_myr = total_fc / x["q"] * F
    # Money-market hedge, step by step
    deposit_fc = total_fc / g(x["if_"], T)        # foreign deposit needed today
    myr_today = deposit_fc / x["q"] * x["S"]      # ringgit converted today
    myr_fv = myr_today * g(x["ih"], T)            # opportunity cost carried to date T
    naive = (x["fixed"] + x["var"]) / x["q"] * x["S"]
    return {
        "real_home": real_h, "real_foreign": real_f, "forward": F, "ppp_spot": ppp,
        "ife_spot": F, "total_cost_fc": total_fc, "forward_hedge_myr": fwd_myr,
        "money_market_myr_fv": myr_fv, "unhedged_expected_myr": total_fc / x["q"] * ppp,
        "naive_myr": naive, "set_aside_today_myr": fwd_myr / g(x["ih"], T),
    }


def main() -> int:
    os.makedirs(os.path.join(ROOT, "evidence"), exist_ok=True)
    rows, fails = [], 0
    for name, x in HAND_INPUTS.items():
        hand = hand_calc(x)
        eng = evaluate(PRESETS[name]).to_dict()
        for k, hv in hand.items():
            ev = D(repr(eng[k]))
            rel = abs(ev - hv) / abs(hv) if hv != 0 else abs(ev - hv)
            ok = rel < D("1e-9")
            fails += (not ok)
            rows.append({"scenario": name, "quantity": k, "independent_value": f"{hv:.10f}",
                         "engine_value": f"{ev:.10f}", "relative_difference": f"{rel:.2E}",
                         "result": "PASS" if ok else "FAIL"})
        # Identity check: forward hedge == money-market hedge (covered IRP)
        same = abs(hand["forward_hedge_myr"] - hand["money_market_myr_fv"]) < D("1e-12")
        fails += (not same)
        rows.append({"scenario": name, "quantity": "identity: forward hedge = money-market hedge",
                     "independent_value": f"{hand['forward_hedge_myr']:.10f}",
                     "engine_value": f"{hand['money_market_myr_fv']:.10f}",
                     "relative_difference": "-", "result": "PASS" if same else "FAIL"})

    csv_path = os.path.join(ROOT, "evidence", "verification_table.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    md_path = os.path.join(ROOT, "evidence", "verification_report.md")
    with open(md_path, "w") as fh:
        fh.write("# RinggitRoute - independent verification evidence\n\n")
        fh.write("All scenario inputs are ILLUSTRATIVE teaching assumptions, not market data.\n\n")
        fh.write("| Scenario | Quantity | Independent (Decimal) | Engine (float) | Rel. diff | Result |\n|---|---|---|---|---|---|\n")
        for r in rows:
            fh.write(f"| {r['scenario']} | {r['quantity']} | {r['independent_value']} | {r['engine_value']} | "
                     f"{r['relative_difference']} | {r['result']} |\n")
        fh.write(f"\n**Checks run: {len(rows)}; failures: {fails}.**\n")

    print(f"{len(rows)} checks, {fails} failure(s). Evidence written to {csv_path} and {md_path}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
