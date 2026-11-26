"""
Unit tests for RinggitRoute (run with:  pytest -q)

They check (1) textbook identities, (2) direction of effects, (3) pinned scenario values
that appear in the report/slides/poster, and (4) the tutor's mistake diagnosis.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.fx_engine import (Scenario, evaluate, fisher_nominal, irp_forward, ppp_expected_spot,  # noqa: E402
                              real_rate_exact, with_change, sensitivity)
from engine.scenarios import SCENARIO_A, SCENARIO_B, SCENARIO_C  # noqa: E402
from engine.tutor import check_rate_answer, check_real_rate_answer, mark_predictions, correct_answers  # noqa: E402


# ---------------- 1. Identities ----------------
def test_fisher_roundtrip():
    r = real_rate_exact(0.06, 0.04)
    assert fisher_nominal(r, 0.04) == pytest.approx(0.06, abs=1e-12)


def test_irp_equal_rates_gives_spot():
    assert irp_forward(5.5, 0.03, 0.03, 1) == pytest.approx(5.5)


@pytest.mark.parametrize("sc", [SCENARIO_A, SCENARIO_B, SCENARIO_C])
def test_money_market_equals_forward(sc):
    r = evaluate(sc)
    assert r.money_market_myr_fv == pytest.approx(r.forward_hedge_myr, rel=1e-12)


def test_ife_equals_ppp_when_real_rates_equal():
    sc = Scenario("t", "XXX", "X", 4.0, 1, 12, fisher_nominal(0.01, 0.05), fisher_nominal(0.01, 0.02),
                  0.05, 0.02, 1000, 0)
    r = evaluate(sc)
    assert r.ife_spot == pytest.approx(r.ppp_spot, rel=1e-12)


# ---------------- 2. Directions ----------------
def test_higher_home_inflation_weakens_myr():
    base = evaluate(SCENARIO_A).ppp_spot
    shocked = evaluate(with_change(SCENARIO_A, "pi_home", 0.06)).ppp_spot
    assert shocked > base


def test_higher_foreign_interest_lowers_forward():
    base = evaluate(SCENARIO_A).forward
    up = evaluate(with_change(SCENARIO_A, "i_foreign", 0.06)).forward
    assert up < base


def test_fisher_link_moves_nominal_rate():
    sc = with_change(SCENARIO_A, "pi_home", 0.05, fisher_link=True)
    assert sc.i_home == pytest.approx(SCENARIO_B.i_home, rel=1e-12)


def test_sensitivity_is_monotonic_in_home_inflation():
    rows = sensitivity(SCENARIO_A, "pi_home", [0.01, 0.02, 0.03, 0.04, 0.05, 0.06], fisher_link=True)
    costs = [r["forward_hedge_myr"] for r in rows]
    assert costs == sorted(costs)


# ---------------- 3. Pinned values used in the documents ----------------
def test_scenario_a_values():
    r = evaluate(SCENARIO_A)
    assert r.forward == pytest.approx(5.447115, abs=5e-7)
    assert r.ppp_spot == pytest.approx(5.446602, abs=5e-7)
    assert r.total_cost_fc == pytest.approx(22_240.0)
    assert r.forward_hedge_myr == pytest.approx(121_143.85, abs=0.01)
    assert r.naive_myr == pytest.approx(121_000.00, abs=0.01)
    assert r.real_home == pytest.approx(0.0098039, abs=5e-8)


def test_scenario_b_values():
    r = evaluate(SCENARIO_B)
    assert SCENARIO_B.i_home == pytest.approx(0.0602941, abs=5e-8)
    assert r.forward == pytest.approx(5.607325, abs=5e-7)
    assert r.ppp_spot == pytest.approx(5.606796, abs=5e-7)


def test_scenario_c_ife_and_ppp_disagree_in_direction():
    r = evaluate(SCENARIO_C)
    assert r.ppp_spot < SCENARIO_C.spot < r.ife_spot


# ---------------- 4. Tutor ----------------
def test_tutor_full_marks_with_key():
    r = evaluate(SCENARIO_A)
    key = correct_answers(SCENARIO_A, r)
    score, fb = mark_predictions(SCENARIO_A, key)
    assert score == 4 and all(f["ok"] for f in fb)


def test_checker_detects_inverted_ratio():
    wrong = SCENARIO_A.spot * 1.04 / 1.03
    assert check_rate_answer(SCENARIO_A, "forward", wrong)["pattern"] == "inverted_ratio"


def test_checker_detects_wrong_variable():
    wrong = ppp_expected_spot(2.9, 0.02, 0.025, 0.5)
    assert check_rate_answer(SCENARIO_C, "forward", wrong)["pattern"] == "wrong_variable"


def test_checker_detects_ignored_horizon():
    wrong = 2.9 * 1.03 / 1.0075
    assert check_rate_answer(SCENARIO_C, "forward", wrong)["pattern"] == "ignored_horizon"


def test_checker_accepts_correct_rounded():
    assert check_rate_answer(SCENARIO_A, "forward", 5.4471)["status"] == "correct"


def test_real_rate_checker_approximation():
    assert check_real_rate_answer(0.03, 0.02, 0.01)["status"] == "acceptable"
