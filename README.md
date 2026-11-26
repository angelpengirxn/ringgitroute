# RinggitRoute — FX Study-Abroad Budget Tutor

GFB3043 / GEB3043 International Financial Management · FinBridge AI Innovation Challenge · Group 19

RinggitRoute helps non-finance university students in Malaysia plan the ringgit cost of an overseas
semester or degree, while learning how **interest rates, inflation and exchange rates** are linked
(Fisher effect, interest rate parity, purchasing power parity and the international Fisher effect).

> **All preset rates are illustrative teaching assumptions, not current market rates or forecasts.**
> This is a learning tool, not financial advice.

## Features

| Tab | What it does | CLO3 link |
|---|---|---|
| ① Learn the triangle | Interest–inflation–FX triangle, direction rules, formulas | Fisher, PPP, IRP, IFE |
| ② Predict → Reveal | Learner predicts four directions, then gets personalised feedback | Direction of effects |
| ③ Budget planner | Step-by-step workings; ringgit cost under naive, forward, money-market and wait strategies | IRP, PPP, hedging extension |
| ④ Sensitivity lab | Vary one input (with/without Fisher link); ±1pp tornado table | Change-of-input analysis |
| ⑤ Check an answer | Verifies a hand-worked or chatbot answer and names the likely mistake | Verified calculations |
| ⑥ Limits & sources | Assumptions, empirical limitations, references | Limitations |

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py              # opens http://localhost:8501
```

## Verify it

```bash
pytest -q                                   # 19 unit tests: identities, directions, pinned values, tutor
python verification/independent_check.py    # Decimal re-computation of every scenario figure
```

Evidence files are written to `evidence/` (`verification_table.csv`, `verification_report.md`,
`pytest_log.txt`).

## Project structure

```
app.py                         Streamlit user interface
ui_components.py               Frosted-glass theme (poster palette) and HTML components
engine/fx_engine.py            Finance engine (pure functions, documented formulas)
engine/scenarios.py            Three illustrative preset scenarios (A, B, C)
engine/tutor.py                Rule-based Predict→Reveal marking and answer-checker
verification/independent_check.py   Independent Decimal-based verification
tests/test_engine.py           Unit tests
evidence/                      Retained calculation evidence
docs/screenshots/              Prototype screenshots used in poster, slides and report
.streamlit/config.toml         Theme
```

## Conventions

* Exchange rates are direct quotes: MYR per 1 unit of foreign currency (per 100 for JPY).
  A higher number means a weaker ringgit.
* Rates are annual decimals and compound once a year; horizon T = months / 12.
