"""
RinggitRoute - rule-based tutoring engine
=========================================

Two learning features:

1. Predict-then-Reveal: before seeing any number, the learner predicts the DIRECTION of
   each effect. The engine marks each prediction and returns a personalised explanation
   that refers to the learner's own inputs.

2. Answer Checker ("Check my / an AI's answer"): the learner pastes a number they worked
   out by hand - or a number given by a chatbot - and the engine compares it with the
   verified calculation. If it is wrong, the engine tests a list of known mistake patterns
   (inverted ratio, linear approximation, wrong variable, ignored horizon, quote-unit slip,
   indirect quote) and names the most likely mistake.

The engine is deterministic: every verdict is traceable to a formula in fx_engine.py.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .fx_engine import Scenario, Result, evaluate, growth, real_rate_exact

REL_TOL = 0.0005   # 0.05% relative tolerance (allows 4-decimal rounding of exchange rates)
REAL_TOL = 0.0001  # 0.01 percentage-point tolerance for real rates


# --------------------------------------------------------------------------------------
# 1. Predict-then-Reveal
# --------------------------------------------------------------------------------------
QUESTIONS = {
    "q_ppp": {
        "text": "Q1. Using inflation only (PPP), over the horizon the ringgit will ... against {cur}",
        "options": ["weaken", "strengthen", "stay the same"],
    },
    "q_irp": {
        "text": "Q2. Using interest rates (IRP), the forward rate will be ... today's spot rate",
        "options": ["above", "below", "equal to"],
    },
    "q_real": {
        "text": "Q3. After removing inflation (Fisher), the higher REAL interest rate is in ...",
        "options": ["Malaysia", "the foreign country", "about equal (within 0.25 percentage points)"],
    },
    "q_budget": {
        "text": "Q4. Compared with a 'today's rate x today's prices' budget, the forward-locked ringgit cost will be ...",
        "options": ["higher", "lower", "the same"],
    },
}


def correct_answers(s: Scenario, r: Result) -> Dict[str, str]:
    ppp = "weaken" if r.ppp_spot > s.spot * (1 + 1e-9) else ("strengthen" if r.ppp_spot < s.spot * (1 - 1e-9) else "stay the same")
    irp = "above" if r.forward > s.spot * (1 + 1e-9) else ("below" if r.forward < s.spot * (1 - 1e-9) else "equal to")
    if abs(r.real_gap) <= 0.0025:
        real = "about equal (within 0.25 percentage points)"
    else:
        real = "Malaysia" if r.real_gap > 0 else "the foreign country"
    gap = r.budget_gap_vs_naive
    budget = "higher" if gap > 0.005 else ("lower" if gap < -0.005 else "the same")
    return {"q_ppp": ppp, "q_irp": irp, "q_real": real, "q_budget": budget}


def mark_predictions(s: Scenario, answers: Dict[str, str]) -> Tuple[int, List[Dict]]:
    """Return (score, feedback list). Each feedback item: question, your answer, correct, ok, why."""
    r = evaluate(s)
    key = correct_answers(s, r)
    cur, ctry = s.currency, s.country
    hi_inf = "Malaysia" if s.pi_home > s.pi_foreign else ctry
    lo_int_ccy = "MYR" if s.i_home < s.i_foreign else cur
    fwd_pos = "above" if r.forward > s.spot else "below"
    why = {
        "q_ppp": (
            f"PPP compares inflation: Malaysia {s.pi_home*100:.2f}% vs {ctry} {s.pi_foreign*100:.2f}%. "
            f"The currency of the country with HIGHER inflation ({hi_inf}) loses purchasing power and is expected to weaken. "
            f"Expected rate: {s.spot:.4f} -> {r.ppp_spot:.4f} MYR per {s.quote_unit} {cur} ({r.ppp_change_total*100:+.2f}%), "
            f"so the ringgit is expected to {key['q_ppp']}."),
        "q_irp": (
            f"IRP compares interest rates: Malaysia {s.i_home*100:.2f}% vs {ctry} {s.i_foreign*100:.2f}%. "
            f"The LOWER-interest currency ({lo_int_ccy}) trades at a forward premium, so nobody earns a risk-free profit "
            f"by borrowing in one currency and depositing in the other. In MYR per {cur} terms the forward is therefore "
            f"{fwd_pos} spot: {r.forward:.4f} ({r.forward_premium_total*100:+.2f}% vs spot)."),
        "q_real": (
            f"Fisher: real rate = (1 + nominal)/(1 + inflation) - 1. Malaysia {r.real_home*100:.2f}%, "
            f"{ctry} {r.real_foreign*100:.2f}% (gap {r.real_gap*100:+.2f} percentage points). "
            "A high nominal rate is not automatically a high real rate - inflation must be removed first."),
        "q_budget": (
            f"The naive budget uses today's spot and today's prices: RM{r.naive_myr:,.2f}. The forward-locked cost is "
            f"RM{r.forward_hedge_myr:,.2f} because (i) living costs rise with {ctry}'s inflation to "
            f"{r.total_cost_fc:,.0f} {cur} and (ii) the forward rate is {r.forward:.4f}, not {s.spot:.4f}."),
    }
    misconception = {
        "q_ppp": "Tip: find the country with the HIGHER inflation first - its currency is the one PPP expects to weaken.",
        "q_irp": "Tip: under IRP the HIGH-interest currency trades at a forward DISCOUNT, not a premium - the interest gain is given back in the forward rate.",
        "q_real": "Tip: compare REAL rates, not nominal ones - divide out inflation before comparing returns.",
        "q_budget": "Tip: a budget at today's exchange rate misses two things - inflation abroad and the expected/locked FX rate.",
    }
    feedback, score = [], 0
    for q, correct in key.items():
        given = answers.get(q)
        ok = given == correct
        score += int(ok)
        text = why[q] if ok else f"You chose '{given}'. {misconception[q]} {why[q]}"
        feedback.append({"question": QUESTIONS[q]["text"].format(cur=cur), "your_answer": given,
                         "correct": correct, "ok": ok, "why": text})
    return score, feedback


# --------------------------------------------------------------------------------------
# 2. Answer checker with mistake diagnosis
# --------------------------------------------------------------------------------------
def _close(a: float, b: float, tol: float = REL_TOL) -> bool:
    return b != 0 and abs(a / b - 1.0) <= tol


def _candidates_rate(s: Scenario, kind: str) -> List[Tuple[str, float, str]]:
    """Candidate values (label, value, explanation) for 'forward' or 'ppp' answers."""
    T, S = s.years, s.spot
    if kind == "forward":
        h, f, var = s.i_home, s.i_foreign, "interest"
        other_h, other_f, other_var = s.pi_home, s.pi_foreign, "inflation"
    else:
        h, f, var = s.pi_home, s.pi_foreign, "inflation"
        other_h, other_f, other_var = s.i_home, s.i_foreign, "interest"
    correct = S * growth(h, T) / growth(f, T)
    c = [
        ("correct", correct, "Matches the verified calculation."),
        ("inverted_ratio", S * growth(f, T) / growth(h, T),
         f"You divided the wrong way. With a direct quote (MYR per foreign unit) the MALAYSIAN {var} rate goes on top: "
         f"S x (1 + {var}_MY)/(1 + {var}_foreign)."),
        ("linear_approx", S * (1 + (h - f) * T),
         f"You used the approximation S x (1 + ({var}_MY - {var}_foreign)). It is close but not exact; the course formula uses the ratio."),
        ("wrong_variable", S * growth(other_h, T) / growth(other_f, T),
         f"You used {other_var} rates. {'IRP/forward rates use INTEREST rates.' if kind == 'forward' else 'PPP uses INFLATION rates.'}"),
        ("indirect_quote", 1 / correct,
         "Your number is the INDIRECT quote (foreign currency per MYR). The app uses MYR per foreign unit."),
        ("quote_unit_x100", correct * 100, "Quote-unit slip: you converted the per-100 quote into per-1 (or the reverse)."),
        ("quote_unit_div100", correct / 100, "Quote-unit slip: you converted the per-100 quote into per-1 (or the reverse)."),
    ]
    if abs(T - 1) > 1e-9:
        c.append(("ignored_horizon", S * (1 + h) / (1 + f),
                  f"You used one full year. The horizon is {s.months} months, so the ratio must be raised to the power T = {T:.4f}."))
        c.append(("simple_interest", S * (1 + h * T) / (1 + f * T),
                  "You de-annualised with simple interest (rate x months/12). Many textbooks accept this for periods "
                  "under one year; RinggitRoute compounds instead. Your method is acceptable if stated - the difference is rounding-level."))
    return c


def check_rate_answer(s: Scenario, kind: str, value: float) -> Dict:
    """kind = 'forward' or 'ppp'. Returns verdict dictionary."""
    cands = _candidates_rate(s, kind)
    correct = cands[0][1]
    matches = [c for c in cands if _close(value, c[1])]
    if matches:
        label, val, msg = min(matches, key=lambda c: abs(value / c[1] - 1))
        status = "correct" if label == "correct" else ("acceptable" if label == "simple_interest" else "mistake")
        return {"status": status, "pattern": label, "message": msg, "correct_value": correct,
                "your_value": value, "error_pct": (value / correct - 1) * 100}
    nearest = min(cands, key=lambda c: abs(value / c[1] - 1))
    return {"status": "unknown", "pattern": None,
            "message": ("The number does not match the verified result or any common mistake pattern. Re-check the inputs "
                        f"and the quote direction. Closest pattern: '{nearest[0]}'."),
            "correct_value": correct, "your_value": value, "error_pct": (value / correct - 1) * 100}


def check_real_rate_answer(nominal: float, inflation: float, value: float) -> Dict:
    """value in DECIMAL (0.0098 for 0.98%)."""
    exact = real_rate_exact(nominal, inflation)
    cands = [
        ("correct", exact, "Matches the exact Fisher relationship (1 + i)/(1 + pi) - 1."),
        ("approximation", nominal - inflation,
         "You used the approximation i - pi. Acceptable for small rates; the exact Fisher value is slightly lower."),
        ("reversed", inflation - nominal, "Sign reversed: real rate = nominal MINUS inflation, not inflation minus nominal."),
        ("inverted_ratio", (1 + inflation) / (1 + nominal) - 1, "Ratio inverted: divide (1 + nominal) by (1 + inflation)."),
        ("added", nominal + inflation, "You added inflation. That gives a NOMINAL rate, not a real rate."),
    ]
    matches = [c for c in cands if abs(value - c[1]) <= REAL_TOL]
    if matches:
        label, val, msg = min(matches, key=lambda c: abs(value - c[1]))
        status = "correct" if label == "correct" else ("acceptable" if label == "approximation" else "mistake")
        return {"status": status, "pattern": label, "message": msg, "correct_value": exact, "your_value": value}
    return {"status": "unknown", "pattern": None,
            "message": "No known pattern matched. Check that percentages were converted to decimals.",
            "correct_value": exact, "your_value": value}
