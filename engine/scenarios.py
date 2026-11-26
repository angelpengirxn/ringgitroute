"""
Preset scenarios used in the demo, report, slides and poster.

ALL NUMBERS BELOW ARE ILLUSTRATIVE TEACHING ASSUMPTIONS. They are NOT current market
rates, NOT forecasts and NOT advice. Users should replace them with the latest figures
from Bank Negara Malaysia (exchange rates, OPR) and the relevant foreign central bank
before making any real decision.
"""
from .fx_engine import Scenario, fisher_nominal, real_rate_exact

# Scenario A - baseline: one-year taught Master's in the United Kingdom
SCENARIO_A = Scenario(
    name="A. UK Master's - baseline",
    currency="GBP", country="the United Kingdom",
    spot=5.5000, quote_unit=1, months=12,
    i_home=0.0300, i_foreign=0.0400,
    pi_home=0.0200, pi_foreign=0.0300,
    fixed_cost_fc=14_000.0,          # tuition fixed in the offer letter
    variable_cost_fc_today=8_000.0,  # rent + food at today's UK prices
    deviation=0.05,
    note="Illustrative. Malaysian inflation and interest rates below the UK's.",
)

# Scenario B - change-of-input: Malaysian inflation jumps to 5%, BNM-style rate response
# keeps the Malaysian REAL rate unchanged (Fisher effect).
_r_home_A = real_rate_exact(SCENARIO_A.i_home, SCENARIO_A.pi_home)
SCENARIO_B = Scenario(
    name="B. UK Master's - Malaysian inflation shock",
    currency="GBP", country="the United Kingdom",
    spot=5.5000, quote_unit=1, months=12,
    i_home=fisher_nominal(_r_home_A, 0.0500),   # = 6.0294%
    i_foreign=0.0400,
    pi_home=0.0500, pi_foreign=0.0300,
    fixed_cost_fc=14_000.0, variable_cost_fc_today=8_000.0,
    deviation=0.05,
    note="Illustrative. Only Malaysian inflation changes (2% -> 5%); the Malaysian nominal rate "
         "follows Fisher so the real rate stays at 0.98%.",
)

# Scenario C - different currency, unit convention and horizon: 6-month exchange in Japan.
# JPY is quoted per 100 yen. Real rates differ across countries, so IFE and PPP disagree.
SCENARIO_C = Scenario(
    name="C. Japan exchange semester - 6 months",
    currency="JPY", country="Japan",
    spot=2.9000, quote_unit=100, months=6,
    i_home=0.0300, i_foreign=0.0075,
    pi_home=0.0200, pi_foreign=0.0250,
    fixed_cost_fc=300_000.0,           # dormitory deposit + insurance (fixed in yen)
    variable_cost_fc_today=900_000.0,  # 6 months x JPY 150,000 living cost at today's prices
    deviation=0.05,
    note="Illustrative. Rate quoted as MYR per 100 JPY. Japan's real rate is negative in this "
         "assumption set, so the interest-based and inflation-based forecasts point in opposite directions.",
)

PRESETS = {s.name: s for s in (SCENARIO_A, SCENARIO_B, SCENARIO_C)}
