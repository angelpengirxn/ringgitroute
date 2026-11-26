# RinggitRoute - independent verification evidence

All scenario inputs are ILLUSTRATIVE teaching assumptions, not market data.

| Scenario | Quantity | Independent (Decimal) | Engine (float) | Rel. diff | Result |
|---|---|---|---|---|---|
| A. UK Master's - baseline | real_home | 0.0098039216 | 0.0098039216 | 3.57E-15 | PASS |
| A. UK Master's - baseline | real_foreign | 0.0097087379 | 0.0097087379 | 4.02E-16 | PASS |
| A. UK Master's - baseline | forward | 5.4471153846 | 5.4471153846 | 1.13E-16 | PASS |
| A. UK Master's - baseline | ppp_spot | 5.4466019417 | 5.4466019417 | 3.39E-17 | PASS |
| A. UK Master's - baseline | ife_spot | 5.4471153846 | 5.4471153846 | 1.13E-16 | PASS |
| A. UK Master's - baseline | total_cost_fc | 22240.0000000000 | 22240.0000000000 | 0.00E+2 | PASS |
| A. UK Master's - baseline | forward_hedge_myr | 121143.8461538462 | 121143.8461538461 | 1.14E-16 | PASS |
| A. UK Master's - baseline | money_market_myr_fv | 121143.8461538462 | 121143.8461538462 | 5.08E-17 | PASS |
| A. UK Master's - baseline | unhedged_expected_myr | 121132.4271844660 | 121132.4271844660 | 7.77E-17 | PASS |
| A. UK Master's - baseline | naive_myr | 121000.0000000000 | 121000.0000000000 | 0.00E+2 | PASS |
| A. UK Master's - baseline | set_aside_today_myr | 117615.3846153846 | 117615.3846153846 | 1.31E-16 | PASS |
| A. UK Master's - baseline | identity: forward hedge = money-market hedge | 121143.8461538462 | 121143.8461538462 | - | PASS |
| B. UK Master's - Malaysian inflation shock | real_home | 0.0098039216 | 0.0098039216 | 3.57E-15 | PASS |
| B. UK Master's - Malaysian inflation shock | real_foreign | 0.0097087379 | 0.0097087379 | 4.02E-16 | PASS |
| B. UK Master's - Malaysian inflation shock | forward | 5.6073246606 | 5.6073246606 | 2.91E-17 | PASS |
| B. UK Master's - Malaysian inflation shock | ppp_spot | 5.6067961165 | 5.6067961165 | 1.13E-16 | PASS |
| B. UK Master's - Malaysian inflation shock | ife_spot | 5.6073246606 | 5.6073246606 | 2.91E-17 | PASS |
| B. UK Master's - Malaysian inflation shock | total_cost_fc | 22240.0000000000 | 22240.0000000000 | 0.00E+2 | PASS |
| B. UK Master's - Malaysian inflation shock | forward_hedge_myr | 124706.9004524887 | 124706.9004524887 | 6.24E-17 | PASS |
| B. UK Master's - Malaysian inflation shock | money_market_myr_fv | 124706.9004524887 | 124706.9004524887 | 6.24E-17 | PASS |
| B. UK Master's - Malaysian inflation shock | unhedged_expected_myr | 124695.1456310680 | 124695.1456310680 | 9.34E-18 | PASS |
| B. UK Master's - Malaysian inflation shock | naive_myr | 121000.0000000000 | 121000.0000000000 | 0.00E+2 | PASS |
| B. UK Master's - Malaysian inflation shock | set_aside_today_myr | 117615.3846153846 | 117615.3846153846 | 4.58E-17 | PASS |
| B. UK Master's - Malaysian inflation shock | identity: forward hedge = money-market hedge | 124706.9004524887 | 124706.9004524887 | - | PASS |
| C. Japan exchange semester - 6 months | real_home | 0.0098039216 | 0.0098039216 | 3.57E-15 | PASS |
| C. Japan exchange semester - 6 months | real_foreign | -0.0170731707 | -0.0170731707 | 5.69E-15 | PASS |
| C. Japan exchange semester - 6 months | forward | 2.9322033315 | 2.9322033315 | 1.56E-16 | PASS |
| C. Japan exchange semester - 6 months | ppp_spot | 2.8929181823 | 2.8929181823 | 1.92E-16 | PASS |
| C. Japan exchange semester - 6 months | ife_spot | 2.9322033315 | 2.9322033315 | 1.56E-16 | PASS |
| C. Japan exchange semester - 6 months | total_cost_fc | 1211180.5529092464 | 1211180.5529092462 | 1.75E-16 | PASS |
| C. Japan exchange semester - 6 months | forward_hedge_myr | 35514.2765227023 | 35514.2765227023 | 2.48E-16 | PASS |
| C. Japan exchange semester - 6 months | money_market_myr_fv | 35514.2765227023 | 35514.2765227023 | 5.29E-16 | PASS |
| C. Japan exchange semester - 6 months | unhedged_expected_myr | 35038.4624361672 | 35038.4624361672 | 4.89E-17 | PASS |
| C. Japan exchange semester - 6 months | naive_myr | 34800.0000000000 | 34800.0000000000 | 0.00E+2 | PASS |
| C. Japan exchange semester - 6 months | set_aside_today_myr | 34993.2564506414 | 34993.2564506414 | 2.61E-16 | PASS |
| C. Japan exchange semester - 6 months | identity: forward hedge = money-market hedge | 35514.2765227023 | 35514.2765227023 | - | PASS |

**Checks run: 36; failures: 0.**
