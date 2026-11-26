"""
RinggitRoute - finance engine
=============================

Pure, side-effect-free functions for the three CLO3 parity relationships used by the
RinggitRoute prototype.

Conventions (applied everywhere in the app, report and slides)
---------------------------------------------------------------
* Exchange rates are DIRECT quotes from a Malaysian point of view:
      S = MYR per `quote_unit` units of foreign currency
  (quote_unit = 1 for GBP/USD/AUD, 100 for JPY).  A HIGHER S means the ringgit is WEAKER.
* Interest and inflation rates are ANNUAL rates in decimal form (3% -> 0.03).
* Horizon T is in YEARS (months / 12). Multi-period rates compound annually:
      growth factor = (1 + rate) ** T
* Subscript h = home (Malaysia, MYR); f = foreign country.

Theories implemented (formulas follow Madura, 2021, ch. 7-8; Eun, Resnick & Chuluun, 2021, ch. 6)
----------------------------------------------------------------------------------------------
Fisher effect          (1 + i) = (1 + r)(1 + pi)                -> r = (1 + i)/(1 + pi) - 1
Interest rate parity   F = S x [(1 + i_h)/(1 + i_f)] ** T
Relative PPP           E[S_T] = S x [(1 + pi_h)/(1 + pi_f)] ** T
International Fisher   E[S_T] = S x [(1 + i_h)/(1 + i_f)] ** T  (same algebra as IRP, but it is a
                       FORECAST of the future spot rate, not a contractual forward rate)
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Dict, List


# --------------------------------------------------------------------------------------
# 1. Core parity formulas
# --------------------------------------------------------------------------------------
def growth(rate: float, years: float) -> float:
    """Compound growth factor (1 + rate) ** years."""
    if rate <= -1:
        raise ValueError("Rate must be greater than -100%.")
    return (1.0 + rate) ** years


def real_rate_exact(nominal: float, inflation: float) -> float:
    """Exact Fisher real rate: r = (1 + i)/(1 + pi) - 1."""
    return (1.0 + nominal) / (1.0 + inflation) - 1.0


def real_rate_approx(nominal: float, inflation: float) -> float:
    """Classroom approximation: r ~ i - pi (good only when rates are small)."""
    return nominal - inflation


def fisher_nominal(real: float, inflation: float) -> float:
    """Nominal rate implied by a real rate and expected inflation: i = (1 + r)(1 + pi) - 1."""
    return (1.0 + real) * (1.0 + inflation) - 1.0


def irp_forward(spot: float, i_home: float, i_foreign: float, years: float) -> float:
    """Interest-rate-parity forward rate (MYR per quote unit of foreign currency)."""
    return spot * growth(i_home, years) / growth(i_foreign, years)


def ppp_expected_spot(spot: float, pi_home: float, pi_foreign: float, years: float) -> float:
    """Relative-PPP forecast of the future spot rate."""
    return spot * growth(pi_home, years) / growth(pi_foreign, years)


def ife_expected_spot(spot: float, i_home: float, i_foreign: float, years: float) -> float:
    """International Fisher Effect forecast of the future spot rate."""
    return spot * growth(i_home, years) / growth(i_foreign, years)


def pct_change(new: float, old: float) -> float:
    """Percentage change from old to new (decimal)."""
    return new / old - 1.0


def annualise(total_change: float, years: float) -> float:
    """Convert a total change over `years` into a compound annual change."""
    return (1.0 + total_change) ** (1.0 / years) - 1.0


# --------------------------------------------------------------------------------------
# 2. Scenario object and full evaluation
# --------------------------------------------------------------------------------------
@dataclass
class Scenario:
    name: str
    currency: str                 # ISO code of the foreign currency, e.g. "GBP"
    country: str                  # e.g. "United Kingdom"
    spot: float                   # MYR per quote_unit of foreign currency (ILLUSTRATIVE)
    quote_unit: int               # 1 or 100
    months: int                   # months until payment
    i_home: float                 # Malaysian nominal interest rate (annual, decimal)
    i_foreign: float              # foreign nominal interest rate
    pi_home: float                # Malaysian expected inflation
    pi_foreign: float             # foreign expected inflation
    fixed_cost_fc: float          # cost already fixed in foreign currency (e.g. tuition)
    variable_cost_fc_today: float  # cost quoted at TODAY's foreign prices (e.g. living costs)
    deviation: float = 0.05       # user-chosen +/- band around the PPP forecast (NOT a statistic)
    bank_margin: float = 0.0      # optional retail FX mark-up on buying foreign currency
    note: str = ""

    @property
    def years(self) -> float:
        return self.months / 12.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Result:
    # Fisher
    real_home: float
    real_foreign: float
    real_home_approx: float
    real_foreign_approx: float
    real_gap: float
    # Exchange-rate outcomes
    forward: float
    forward_premium_total: float
    forward_premium_annual: float
    ppp_spot: float
    ppp_change_total: float
    ife_spot: float
    ife_change_total: float
    ppp_vs_ife_gap: float
    # Foreign-currency need
    variable_cost_fc_future: float
    total_cost_fc: float
    naive_cost_fc: float
    # MYR outcomes
    naive_myr: float
    forward_hedge_myr: float
    money_market_fc_deposit_today: float
    money_market_myr_today: float
    money_market_myr_fv: float
    unhedged_expected_myr: float
    unhedged_low_myr: float
    unhedged_high_myr: float
    set_aside_today_myr: float
    budget_gap_vs_naive: float
    myr_direction: str
    explanations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


def _to_myr(amount_fc: float, rate: float, quote_unit: int, margin: float = 0.0) -> float:
    """Convert a foreign-currency amount into MYR at `rate` (MYR per quote_unit)."""
    return amount_fc / quote_unit * rate * (1.0 + margin)


def evaluate(s: Scenario) -> Result:
    """Run every CLO3 calculation for one scenario and return a Result."""
    T = s.years
    if T <= 0:
        raise ValueError("Horizon must be at least one month.")
    if s.spot <= 0:
        raise ValueError("Spot rate must be positive.")

    # --- Fisher effect ---
    r_h = real_rate_exact(s.i_home, s.pi_home)
    r_f = real_rate_exact(s.i_foreign, s.pi_foreign)

    # --- Parity conditions ---
    F = irp_forward(s.spot, s.i_home, s.i_foreign, T)
    ppp = ppp_expected_spot(s.spot, s.pi_home, s.pi_foreign, T)
    ife = ife_expected_spot(s.spot, s.i_home, s.i_foreign, T)
    prem_total = pct_change(F, s.spot)

    # --- Foreign-currency amount needed at T ---
    var_future = s.variable_cost_fc_today * growth(s.pi_foreign, T)
    total_fc = s.fixed_cost_fc + var_future
    naive_fc = s.fixed_cost_fc + s.variable_cost_fc_today

    # --- MYR cost under each strategy (all measured in MYR at date T) ---
    naive = _to_myr(naive_fc, s.spot, s.quote_unit, s.bank_margin)
    fwd = _to_myr(total_fc, F, s.quote_unit, s.bank_margin)
    mm_fc_today = total_fc / growth(s.i_foreign, T)
    mm_myr_today = _to_myr(mm_fc_today, s.spot, s.quote_unit, s.bank_margin)
    mm_myr_fv = mm_myr_today * growth(s.i_home, T)
    unhedged = _to_myr(total_fc, ppp, s.quote_unit, s.bank_margin)
    low = _to_myr(total_fc, ppp * (1 - s.deviation), s.quote_unit, s.bank_margin)
    high = _to_myr(total_fc, ppp * (1 + s.deviation), s.quote_unit, s.bank_margin)
    set_aside = fwd / growth(s.i_home, T)

    direction = "weakens" if ppp > s.spot else ("strengthens" if ppp < s.spot else "is unchanged")

    res = Result(
        real_home=r_h, real_foreign=r_f,
        real_home_approx=real_rate_approx(s.i_home, s.pi_home),
        real_foreign_approx=real_rate_approx(s.i_foreign, s.pi_foreign),
        real_gap=r_h - r_f,
        forward=F, forward_premium_total=prem_total,
        forward_premium_annual=annualise(prem_total, T),
        ppp_spot=ppp, ppp_change_total=pct_change(ppp, s.spot),
        ife_spot=ife, ife_change_total=pct_change(ife, s.spot),
        ppp_vs_ife_gap=ife / ppp - 1.0,
        variable_cost_fc_future=var_future, total_cost_fc=total_fc, naive_cost_fc=naive_fc,
        naive_myr=naive, forward_hedge_myr=fwd,
        money_market_fc_deposit_today=mm_fc_today, money_market_myr_today=mm_myr_today,
        money_market_myr_fv=mm_myr_fv,
        unhedged_expected_myr=unhedged, unhedged_low_myr=low, unhedged_high_myr=high,
        set_aside_today_myr=set_aside, budget_gap_vs_naive=fwd - naive,
        myr_direction=direction,
    )
    res.explanations = explain(s, res)
    return res


# --------------------------------------------------------------------------------------
# 3. Plain-language interpretation (beginner level)
# --------------------------------------------------------------------------------------
def _pp(x: float) -> str:
    return f"{x * 100:.2f}%"


def explain(s: Scenario, r: Result) -> List[str]:
    cur = s.currency
    unit = f"{s.quote_unit} {cur}" if s.quote_unit != 1 else f"1 {cur}"
    out = []
    # Inflation -> FX (PPP)
    if s.pi_home > s.pi_foreign:
        out.append(
            f"Inflation: Malaysian prices are assumed to rise faster ({_pp(s.pi_home)}) than prices in "
            f"{s.country} ({_pp(s.pi_foreign)}). PPP says the ringgit must lose purchasing power, so the "
            f"rate is expected to move from RM{s.spot:.4f} to RM{r.ppp_spot:.4f} per {unit} "
            f"({_pp(r.ppp_change_total)}): the ringgit WEAKENS and your bill in ringgit rises.")
    elif s.pi_home < s.pi_foreign:
        out.append(
            f"Inflation: Malaysian inflation ({_pp(s.pi_home)}) is below {s.country}'s ({_pp(s.pi_foreign)}). "
            f"PPP expects the ringgit to STRENGTHEN from RM{s.spot:.4f} to RM{r.ppp_spot:.4f} per {unit} "
            f"({_pp(r.ppp_change_total)}), which partly offsets higher prices abroad.")
    else:
        out.append("Inflation: both countries have the same expected inflation, so PPP predicts no change in the rate.")
    # Interest -> forward (IRP)
    if s.i_home < s.i_foreign:
        out.append(
            f"Interest: the {cur} deposit pays more ({_pp(s.i_foreign)}) than a ringgit deposit ({_pp(s.i_home)}). "
            f"IRP removes that 'free' gain: the forward rate RM{r.forward:.4f} sits BELOW spot "
            f"(forward discount of {_pp(r.forward_premium_total)}), so locking the rate today is slightly cheaper than spot.")
    elif s.i_home > s.i_foreign:
        out.append(
            f"Interest: a ringgit deposit pays more ({_pp(s.i_home)}) than a {cur} deposit ({_pp(s.i_foreign)}). "
            f"IRP sets the forward rate ABOVE spot at RM{r.forward:.4f} (forward premium of "
            f"{_pp(r.forward_premium_total)}): you 'pay back' the extra ringgit interest when you lock the rate.")
    else:
        out.append("Interest: equal interest rates mean the forward rate equals the spot rate under IRP.")
    # Fisher link
    out.append(
        f"Fisher: real (after-inflation) rates are {_pp(r.real_home)} in Malaysia and {_pp(r.real_foreign)} in "
        f"{s.country}. " + (
            "They are almost equal, so the interest-rate forecast (IFE) and the inflation forecast (PPP) agree."
            if abs(r.real_gap) < 0.0025 else
            f"They differ by {_pp(r.real_gap)}, so IFE ({r.ife_spot:.4f}) and PPP ({r.ppp_spot:.4f}) disagree by "
            f"{_pp(r.ppp_vs_ife_gap)}. IFE only matches PPP when real rates are equal across countries."))
    # Budget message
    out.append(
        f"Budget: a 'today's rate' budget of RM{r.naive_myr:,.2f} misses foreign inflation and the expected FX move. "
        f"Locking with a forward costs RM{r.forward_hedge_myr:,.2f} (difference RM{r.budget_gap_vs_naive:,.2f}). "
        f"If you wait, the PPP-based expectation is RM{r.unhedged_expected_myr:,.2f}, but a +/-{s.deviation*100:.0f}% "
        f"deviation (your assumption) gives RM{r.unhedged_low_myr:,.2f} to RM{r.unhedged_high_myr:,.2f}.")
    out.append(
        f"No free lunch: converting now and saving in {cur} (money-market hedge) costs RM{r.money_market_myr_fv:,.2f} "
        f"in date-T ringgit - the same as the forward (RM{r.forward_hedge_myr:,.2f}) because covered IRP holds in this model.")
    return out


# --------------------------------------------------------------------------------------
# 4. Sensitivity analysis
# --------------------------------------------------------------------------------------
PARAMS = {
    "pi_home": "Malaysian inflation",
    "pi_foreign": "Foreign inflation",
    "i_home": "Malaysian interest rate",
    "i_foreign": "Foreign interest rate",
    "months": "Horizon (months)",
    "spot": "Spot rate today",
}


def with_change(s: Scenario, param: str, value: float, fisher_link: bool = False) -> Scenario:
    """Return a copy of the scenario with one input changed.

    fisher_link=True keeps the REAL interest rate of that country constant, so a change in
    inflation passes through to the nominal interest rate (Fisher effect)."""
    d = s.to_dict()
    if fisher_link and param in ("pi_home", "pi_foreign"):
        side = "home" if param == "pi_home" else "foreign"
        r = real_rate_exact(d[f"i_{side}"], d[param])
        d[f"i_{side}"] = fisher_nominal(r, value)
    d[param] = int(value) if param == "months" else value
    return Scenario(**d)


def sensitivity(s: Scenario, param: str, values: List[float], fisher_link: bool = False) -> List[Dict]:
    rows = []
    for v in values:
        sc = with_change(s, param, v, fisher_link)
        r = evaluate(sc)
        rows.append({
            "value": v, "i_home": sc.i_home, "i_foreign": sc.i_foreign,
            "forward": r.forward, "ppp_spot": r.ppp_spot, "ife_spot": r.ife_spot,
            "forward_hedge_myr": r.forward_hedge_myr,
            "unhedged_expected_myr": r.unhedged_expected_myr,
        })
    return rows


def tornado(s: Scenario, shock: float = 0.01) -> List[Dict]:
    """One-at-a-time +/- shock (in percentage points) to each rate; impact on forward-hedged MYR cost."""
    base = evaluate(s).forward_hedge_myr
    base_ppp = evaluate(s).unhedged_expected_myr
    rows = []
    for p in ("i_home", "i_foreign", "pi_home", "pi_foreign"):
        up = evaluate(with_change(s, p, getattr(s, p) + shock))
        dn = evaluate(with_change(s, p, getattr(s, p) - shock))
        rows.append({
            "input": PARAMS[p],
            "fwd_down": dn.forward_hedge_myr - base, "fwd_up": up.forward_hedge_myr - base,
            "ppp_down": dn.unhedged_expected_myr - base_ppp, "ppp_up": up.unhedged_expected_myr - base_ppp,
        })
    return rows
