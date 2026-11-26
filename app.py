"""
RinggitRoute - FX Study-Abroad Budget Tutor

Run locally:   pip install -r requirements.txt
               streamlit run app.py
"""
from dataclasses import replace

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui_components as ui
from engine.fx_engine import Scenario, evaluate, sensitivity, tornado, PARAMS
from engine.scenarios import PRESETS
from engine.tutor import QUESTIONS, mark_predictions, check_rate_answer, check_real_rate_answer

st.set_page_config(page_title="RinggitRoute - FX Study-Abroad Budget Tutor", page_icon="🧭", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)

PLOT_FONT = dict(family="Gabarito, Inter, Arial, sans-serif", color=ui.INK, size=13)


def glass_layout(fig, height):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), font=PLOT_FONT,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", y=1.14, bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="rgba(29,33,39,0.08)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(29,33,39,0.08)", zeroline=False)
    return fig


def pct(x, d=2):
    return f"{x*100:.{d}f}%"


def unit_label(s: Scenario):
    return f"MYR per {s.quote_unit} {s.currency}"


# ---------------------------------------------------------------- sidebar: grouped inputs
st.sidebar.markdown("## 🧭 RinggitRoute")
st.sidebar.caption("FX study-abroad budget tutor for non-finance students")
preset_name = st.sidebar.selectbox("Start from a scenario", list(PRESETS.keys()), key="preset")
base = PRESETS[preset_name]

if st.session_state.get("_loaded") != preset_name:      # reset widgets when preset changes
    st.session_state.update({
        "spot": base.spot, "months": base.months,
        "i_home": base.i_home * 100, "i_foreign": base.i_foreign * 100,
        "pi_home": base.pi_home * 100, "pi_foreign": base.pi_foreign * 100,
        "fixed": base.fixed_cost_fc, "var": base.variable_cost_fc_today,
        "dev": base.deviation * 100, "margin": base.bank_margin * 100, "_loaded": preset_name,
    })

st.sidebar.markdown(
    "<div class='rr-banner'><b>Illustrative data.</b> Preset rates are teaching assumptions, "
    "<u>not</u> current market rates or forecasts. Replace them with the latest Bank Negara Malaysia "
    "figures before any real decision.</div>", unsafe_allow_html=True)

country = base.country.replace("the ", "").title()
with st.sidebar.expander("Exchange rate & horizon", expanded=True):
    st.number_input(f"Spot rate today ({unit_label(base)})", min_value=0.0001, step=0.01, format="%.4f", key="spot")
    st.slider("Months until you pay", 1, 36, key="months")
with st.sidebar.expander("Interest rates (% per year)", expanded=True):
    st.number_input("Malaysia - ringgit deposit rate", step=0.25, format="%.4f", key="i_home")
    st.number_input(f"{country} - {base.currency} deposit rate", step=0.25, format="%.4f", key="i_foreign")
with st.sidebar.expander("Expected inflation (% per year)", expanded=True):
    st.number_input("Malaysia", step=0.25, format="%.4f", key="pi_home")
    st.number_input(country, step=0.25, format="%.4f", key="pi_foreign")
with st.sidebar.expander(f"Your costs (in {base.currency})", expanded=False):
    st.number_input("Fixed cost (e.g. tuition in offer letter)", min_value=0.0, step=500.0, key="fixed")
    st.number_input("Living cost at TODAY's prices", min_value=0.0, step=500.0, key="var")
with st.sidebar.expander("FX mark-up & what-if band", expanded=False):
    st.slider("What-if band around PPP forecast (+/- %)", 0.0, 20.0, step=0.5, key="dev",
              help="Your own assumption for how far the actual rate could miss the PPP forecast. Not a statistic.")
    st.slider("Bank FX mark-up (%)", 0.0, 5.0, step=0.1, key="margin",
              help="Retail providers add a margin to the mid-market rate. Set 0 to match textbook results.")

edited = any(abs(a - b) > 1e-12 for a, b in [
    (st.session_state.spot, base.spot), (st.session_state.i_home / 100, base.i_home),
    (st.session_state.i_foreign / 100, base.i_foreign), (st.session_state.pi_home / 100, base.pi_home),
    (st.session_state.pi_foreign / 100, base.pi_foreign), (st.session_state.months, base.months),
    (st.session_state.fixed, base.fixed_cost_fc), (st.session_state.var, base.variable_cost_fc_today)])
S = replace(base, spot=st.session_state.spot, months=int(st.session_state.months),
            i_home=st.session_state.i_home / 100, i_foreign=st.session_state.i_foreign / 100,
            pi_home=st.session_state.pi_home / 100, pi_foreign=st.session_state.pi_foreign / 100,
            fixed_cost_fc=st.session_state.fixed, variable_cost_fc_today=st.session_state.var,
            deviation=st.session_state.dev / 100, bank_margin=st.session_state.margin / 100,
            name=preset_name + (" (edited)" if edited else ""))
R = evaluate(S)

# ---------------------------------------------------------------- header + answer up front
st.markdown(
    "<div class='rr-hero'><div class='rr-title'>RinggitRoute</div>"
    "<div class='rr-tag'>Know what your overseas semester really costs in ringgit — before the ringgit moves.</div>"
    "<div class='rr-sub'>Interest rates, inflation and exchange rates explained with your own study-abroad budget.</div>"
    "</div>", unsafe_allow_html=True)
st.markdown(ui.headline(R.forward_hedge_myr, R.set_aside_today_myr, R.budget_gap_vs_naive, S.months, S.i_home),
            unsafe_allow_html=True)
st.caption(f"Active scenario: **{S.name}** · {S.note}")

tabs = st.tabs(["① Learn the triangle", "② Predict → Reveal", "③ Budget planner",
                "④ Sensitivity lab", "⑤ Check an answer", "⑥ Limits & sources"])

# ================================================================ TAB 1: LEARN
with tabs[0]:
    c1, c2 = st.columns([1.05, 1])
    with c1:
        with st.container(border=True):
            st.subheader("Three numbers, one triangle")
            st.markdown("Your bill abroad is in **foreign currency**, but your savings are in **ringgit**. "
                        "Three economic forces decide how many ringgit you will need:")
            fig = go.Figure()
            pts = {"Interest rate": (0.5, 0.95), "Inflation": (0.08, 0.12), "Exchange rate": (0.92, 0.12)}
            for (a, b, lab) in [("Inflation", "Interest rate", "Fisher effect"),
                                ("Inflation", "Exchange rate", "PPP"),
                                ("Interest rate", "Exchange rate", "IRP / IFE")]:
                (x0, y0), (x1, y1) = pts[a], pts[b]
                fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines",
                                         line=dict(color=ui.YELLOW, width=6), hoverinfo="skip", showlegend=False))
                fig.add_annotation(x=(x0 + x1) / 2, y=(y0 + y1) / 2, text=f"<b>{lab}</b>", showarrow=False,
                                   font=dict(size=14, color=ui.INK), bgcolor="rgba(255,255,255,0.85)",
                                   bordercolor=ui.YELLOW, borderpad=4)
            for k, (x, y) in pts.items():
                fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text", text=[f"<b>{k}</b>"],
                                         textposition="top center" if y > .5 else "bottom center",
                                         marker=dict(size=34, color=ui.INK), textfont=dict(size=15, color=ui.INK),
                                         hoverinfo="skip", showlegend=False))
            glass_layout(fig, 320)
            fig.update_xaxes(visible=False, range=[-0.1, 1.1])
            fig.update_yaxes(visible=False, range=[-0.15, 1.15])
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        with st.container(border=True):
            st.subheader("Direction rules (memorise these)")
            st.markdown(
                "| If ... | then ... | Theory |\n|---|---|---|\n"
                "| Malaysian inflation rises vs abroad | ringgit expected to **weaken** (RM per foreign unit ↑) | PPP |\n"
                "| Inflation expected to rise | nominal interest rates **rise** to protect the real return | Fisher |\n"
                "| Ringgit interest rate is **lower** than foreign | forward rate is **below** spot (foreign currency at a discount) | IRP |\n"
                "| Ringgit interest rate is **higher** than foreign | ringgit expected to **weaken** by the gap | IFE |\n")
            st.info("**Quote convention used everywhere:** RM per 1 foreign unit (per 100 for JPY). "
                    "A **higher** number means a **weaker** ringgit and a **bigger** bill for you.")
    with st.container(border=True):
        st.subheader("The formulas behind every number")
        f1, f2 = st.columns(2)
        with f1:
            st.markdown("**Fisher effect** (real vs nominal)")
            st.latex(r"1+i = (1+r)(1+\pi) \;\Rightarrow\; r=\frac{1+i}{1+\pi}-1 \;\approx\; i-\pi")
            st.markdown("**Interest rate parity** (contract you can lock today)")
            st.latex(r"F = S\left(\frac{1+i_{MY}}{1+i_{f}}\right)^{T}")
        with f2:
            st.markdown("**Relative PPP** (inflation-based forecast)")
            st.latex(r"E[S_T] = S\left(\frac{1+\pi_{MY}}{1+\pi_{f}}\right)^{T}")
            st.markdown("**International Fisher effect** (interest-based forecast)")
            st.latex(r"E[S_T] = S\left(\frac{1+i_{MY}}{1+i_{f}}\right)^{T}")
        st.caption("T = months/12. Rates are annual and compound once a year. Sources: Madura (2021); "
                   "Eun, Resnick & Chuluun (2021); Fisher (1930).")

# ================================================================ TAB 2: PREDICT -> REVEAL
with tabs[1]:
    st.subheader("Guided example: predict first, then see why")
    st.markdown(
        f"**Your situation:** you will pay **{S.fixed_cost_fc:,.0f} {S.currency}** fixed costs plus living costs of "
        f"**{S.variable_cost_fc_today:,.0f} {S.currency}** (today's prices) in **{S.months} months**. "
        f"Today the rate is **{S.spot:.4f} {unit_label(S)}**.")
    g1, g2, g3 = st.columns(3)
    g1.metric("Interest: Malaysia vs abroad", f"{pct(S.i_home)} vs {pct(S.i_foreign)}")
    g2.metric("Inflation: Malaysia vs abroad", f"{pct(S.pi_home)} vs {pct(S.pi_foreign)}")
    g3.metric("Horizon", f"{S.months} months (T = {S.years:.2f})")
    with st.form("predict"):
        ans = {}
        for q, meta in QUESTIONS.items():
            ans[q] = st.radio(meta["text"].format(cur=S.currency), meta["options"], index=None, key=f"p_{q}",
                              horizontal=True)
        submitted = st.form_submit_button("Reveal the answers")
    if submitted:
        if any(v is None for v in ans.values()):
            st.warning("Answer all four questions first - committing to a prediction is what makes it stick.")
        else:
            score, fb = mark_predictions(S, ans)
            st.markdown(ui.score_row(score, [f["ok"] for f in fb]), unsafe_allow_html=True)
            st.markdown(ui.question_cards(fb), unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("#### What this means for you")
                st.markdown(ui.tagged_notes(R.explanations), unsafe_allow_html=True)

# ================================================================ TAB 3: BUDGET PLANNER
with tabs[2]:
    st.subheader("Step-by-step workings")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"<div class='rr-card'><h4><span class='rr-step'>1</span>Real rates (Fisher)</h4>"
                    f"<div class='rr-small'>Malaysia</div><div class='rr-big'>{pct(R.real_home)}</div>"
                    f"<div class='rr-small'>{country}: <b>{pct(R.real_foreign)}</b><br>"
                    f"approx. i−π: {pct(R.real_home_approx)} / {pct(R.real_foreign_approx)}</div></div>",
                    unsafe_allow_html=True)
    with s2:
        st.markdown(f"<div class='rr-card'><h4><span class='rr-step'>2</span>Forward rate (IRP)</h4>"
                    f"<div class='rr-small'>{unit_label(S)}</div><div class='rr-big'>{R.forward:.4f}</div>"
                    f"<div class='rr-small'>{'premium' if R.forward_premium_total > 0 else 'discount'} "
                    f"{pct(R.forward_premium_total)} over {S.months} m<br>({pct(R.forward_premium_annual)} p.a.)</div></div>",
                    unsafe_allow_html=True)
    with s3:
        st.markdown(f"<div class='rr-card'><h4><span class='rr-step'>3</span>Expected spot (PPP)</h4>"
                    f"<div class='rr-small'>{unit_label(S)}</div><div class='rr-big'>{R.ppp_spot:.4f}</div>"
                    f"<div class='rr-small'>ringgit {R.myr_direction} ({pct(R.ppp_change_total)})<br>"
                    f"IFE forecast: <b>{R.ife_spot:.4f}</b></div></div>", unsafe_allow_html=True)
    with s4:
        st.markdown(f"<div class='rr-card'><h4><span class='rr-step'>4</span>Foreign amount needed</h4>"
                    f"<div class='rr-small'>{S.currency} at month {S.months}</div>"
                    f"<div class='rr-big'>{R.total_cost_fc:,.0f}</div>"
                    f"<div class='rr-small'>= {S.fixed_cost_fc:,.0f} fixed + {S.variable_cost_fc_today:,.0f} × "
                    f"(1+{pct(S.pi_foreign)})^{S.years:.2f}</div></div>", unsafe_allow_html=True)

    st.subheader("How many ringgit will you need?")
    with st.container(border=True):
        rows = [
            dict(label="Naive budget (today's rate × today's prices)", value=R.naive_myr, kind="naive",
                 note="Ignores inflation abroad and FX movement"),
            dict(label="Lock a forward contract today", value=R.forward_hedge_myr, kind="lock",
                 note="Certain cost; rate fixed by IRP"),
            dict(label="Convert now + save in foreign deposit (money-market hedge)", value=R.money_market_myr_fv,
                 kind="lock", note=f"Convert {ui.rm(R.money_market_myr_today)} today; value shown at month {S.months}"),
            dict(label="Wait and convert later: PPP expectation", value=R.unhedged_expected_myr, kind="wait",
                 note="Expected, not guaranteed", band=True),
            dict(label=f"Wait: rate {S.deviation*100:.1f}% better than PPP", value=R.unhedged_low_myr, kind="wait",
                 note="Your what-if assumption"),
            dict(label=f"Wait: rate {S.deviation*100:.1f}% worse than PPP", value=R.unhedged_high_myr, kind="wait",
                 note="Your what-if assumption"),
        ]
        st.markdown(ui.ruled_bill(rows, (R.unhedged_low_myr, R.unhedged_high_myr), S.deviation),
                    unsafe_allow_html=True)
    st.markdown(ui.fund_band(R.set_aside_today_myr, S.i_home, R.budget_gap_vs_naive), unsafe_allow_html=True)

    with st.expander("Show every formula with your numbers substituted"):
        T = S.years
        st.latex(rf"r_{{MY}}=\frac{{1+{S.i_home:.4f}}}{{1+{S.pi_home:.4f}}}-1={R.real_home:.6f}")
        st.latex(rf"F={S.spot:.4f}\times\left(\frac{{1+{S.i_home:.4f}}}{{1+{S.i_foreign:.4f}}}\right)^{{{T:.4f}}}={R.forward:.6f}")
        st.latex(rf"E[S_T]_{{PPP}}={S.spot:.4f}\times\left(\frac{{1+{S.pi_home:.4f}}}{{1+{S.pi_foreign:.4f}}}\right)^{{{T:.4f}}}={R.ppp_spot:.6f}")
        st.latex(rf"\text{{Cost}}_{{FC}}={S.fixed_cost_fc:,.0f}+{S.variable_cost_fc_today:,.0f}(1+{S.pi_foreign:.4f})^{{{T:.4f}}}={R.total_cost_fc:,.2f}")
        st.latex(rf"\text{{Forward cost}}=\frac{{{R.total_cost_fc:,.2f}}}{{{S.quote_unit}}}\times{R.forward:.6f}"
                 + (rf"\times(1+{S.bank_margin:.4f})" if S.bank_margin else "") + rf"=RM\,{R.forward_hedge_myr:,.2f}")
        st.caption("Every value above is re-computed independently in verification/independent_check.py.")
    with st.container(border=True):
        st.markdown("#### Plain-language interpretation")
        st.markdown(ui.tagged_notes(R.explanations), unsafe_allow_html=True)

# ================================================================ TAB 4: SENSITIVITY
with tabs[3]:
    st.subheader("Change one input, watch the bill move")
    a, b = st.columns([1, 2])
    with a:
        with st.container(border=True):
            param = st.selectbox("Input to vary", ["pi_home", "pi_foreign", "i_home", "i_foreign"],
                                 format_func=lambda p: PARAMS[p])
            link = st.checkbox("Apply Fisher effect (interest rate follows inflation)", value=True,
                               help="Keeps that country's REAL rate constant, so higher inflation also raises its nominal rate.")
            lo_v, hi_v = st.slider("Range (% per year)", -2.0, 15.0, (0.0, 8.0), step=0.5)
    vals = [x / 100 for x in pd.Series(range(int(lo_v * 4), int(hi_v * 4) + 1)) / 4]
    rows_on = pd.DataFrame(sensitivity(S, param, vals, fisher_link=True))
    rows_off = pd.DataFrame(sensitivity(S, param, vals, fisher_link=False))
    is_pi = param.startswith("pi")
    active = rows_on if link else rows_off
    run = active["forward_hedge_myr"].iloc[-1] - active["forward_hedge_myr"].iloc[0]
    run_ppp = active["unhedged_expected_myr"].iloc[-1] - active["unhedged_expected_myr"].iloc[0]
    with a:
        st.markdown(f"<div class='rr-running'>Forward cost <span>{run:+,.2f}</span> RM from {lo_v:g}% to {hi_v:g}%</div>"
                    f"<div class='rr-small'>PPP expectation moves {run_ppp:+,.2f} RM over the same range.</div>",
                    unsafe_allow_html=True)
    with b:
        with st.container(border=True):
            fig = go.Figure()
            if is_pi:
                # Both forward paths are shown; the one matching the checkbox is drawn solid, the other faded.
                fig.add_trace(go.Scatter(x=rows_off["value"] * 100, y=rows_off["forward_hedge_myr"],
                                         name="Forward, Fisher link OFF", line=dict(color=ui.RED, width=3),
                                         opacity=0.45 if link else 1))
                fig.add_trace(go.Scatter(x=rows_on["value"] * 100, y=rows_on["forward_hedge_myr"],
                                         name="Forward-locked, Fisher link ON", line=dict(color=ui.BLUE, width=4),
                                         opacity=1 if link else 0.45))
            else:
                fig.add_trace(go.Scatter(x=active["value"] * 100, y=active["forward_hedge_myr"],
                                         name="Forward-locked cost (IRP)", line=dict(color=ui.BLUE, width=4)))
            fig.add_trace(go.Scatter(x=active["value"] * 100, y=active["unhedged_expected_myr"],
                                     name="Wait: PPP expectation", line=dict(color=ui.INK, width=2.5, dash="dash")))
            fig.add_vline(x=getattr(S, param) * 100, line=dict(color=ui.YELLOW, width=3, dash="dot"),
                          annotation_text="current input")
            glass_layout(fig, 380)
            fig.update_layout(xaxis_title=f"{PARAMS[param]} (% per year)", yaxis_title="RM needed at payment date")
            st.plotly_chart(fig, use_container_width=True)
    if is_pi and not link:
        st.warning("Fisher link is OFF: inflation changes PPP but not interest rates, so the forward (IRP) line stays "
                   "flat while the PPP line moves. The gap you see is a real-interest-rate difference - exactly when "
                   "IFE and PPP stop agreeing.")
    st.markdown("#### One-at-a-time ±1 percentage point shock (tornado)")
    with st.container(border=True):
        st.markdown(ui.tornado_bars(tornado(S, 0.01)), unsafe_allow_html=True)
    st.caption("Values are changes in RM versus the current scenario. Shocks are applied without the Fisher link, "
               "to isolate each variable.")

# ================================================================ TAB 5: CHECK AN ANSWER
with tabs[4]:
    st.subheader("Check my answer - or check what a chatbot told me")
    st.markdown("Work out a number by hand (or paste one from ChatGPT/Gemini). RinggitRoute compares it with the "
                "verified calculation for the **active scenario** and names the most likely mistake.")
    k1, k2 = st.columns(2)
    with k1:
        with st.container(border=True):
            kind = st.radio("What did you calculate?", ["IRP forward rate", "PPP expected spot rate",
                                                         "Malaysian real interest rate (%)"])
            val = st.number_input("Your answer", value=0.0, format="%.6f")
            go_btn = st.button("Check")
        st.markdown("**Try these**")
        inverted = S.spot * (1 + S.i_foreign) ** S.years / (1 + S.i_home) ** S.years
        st.markdown(ui.try_cards(inverted, (S.i_home - S.pi_home) * 100, R.forward), unsafe_allow_html=True)
    with k2:
        if go_btn and val != 0:
            if kind.startswith("Malaysian"):
                v = check_real_rate_answer(S.i_home, S.pi_home, val / 100)
                shown = f"{v['correct_value']*100:.4f}%"
            else:
                v = check_rate_answer(S, "forward" if kind.startswith("IRP") else "ppp", val)
                shown = f"{v['correct_value']:.6f} {unit_label(S)}"
            st.markdown(ui.result_card(v["status"], v["message"], shown), unsafe_allow_html=True)
        else:
            st.markdown("<div class='rr-card'><h4>How it works</h4><div class='rr-small'>Pick what you calculated, type "
                        "your number and press <b>Check</b>. The verdict card names the mistake pattern - inverted "
                        "ratio, linear shortcut, wrong variable, ignored horizon, indirect quote or per-100 yen slip - "
                        "and shows the verified value.</div></div>", unsafe_allow_html=True)
    st.caption("Why this matters: the assignment brief requires AI-generated answers to be checked against "
               "independently verified calculations. This tab makes that check part of the learning loop.")

# ================================================================ TAB 6: LIMITS & SOURCES
with tabs[5]:
    l1, l2 = st.columns(2)
    with l1:
        with st.container(border=True):
            st.subheader("Assumptions in this model")
            st.markdown(
                "- Rates are annual, compound once a year, and stay constant over the horizon.\n"
                "- Mid-market rates; no bid-ask spread unless you add a bank mark-up.\n"
                "- Covered IRP holds exactly (no arbitrage, no capital controls, equal credit risk).\n"
                "- PPP and IFE are treated as **expectations**, not promises.\n"
                "- Living costs rise with the foreign country's general inflation rate.")
        with st.container(border=True):
            st.subheader("Known limitations")
            st.markdown(
                "- **PPP works poorly in the short run.** Deviations from PPP die out only slowly (Rogoff, 1996; "
                "Taylor & Taylor, 2004).\n"
                "- **Forward rates are poor forecasts.** Forward premiums mostly reflect risk premiums (Fama, 1984), and "
                "a random walk often forecasts as well as economic models (Meese & Rogoff, 1983).\n"
                "- **Covered IRP can deviate** in real markets because of bank balance-sheet constraints "
                "(Du, Tepper & Verdelhan, 2018).\n"
                "- Retail customers pay spreads and may face product eligibility rules; check with a licensed bank.\n"
                "- This is a learning tool, **not financial advice**.")
    with l2:
        with st.container(border=True):
            st.subheader("References")
            st.markdown(
                "- Du, W., Tepper, A., & Verdelhan, A. (2018). Deviations from covered interest rate parity. "
                "*Journal of Finance, 73*(3), 915-957. https://doi.org/10.1111/jofi.12620\n"
                "- Eun, C. S., Resnick, B. G., & Chuluun, T. (2021). *International financial management* (9th ed.). McGraw-Hill.\n"
                "- Fama, E. F. (1984). Forward and spot exchange rates. *Journal of Monetary Economics, 14*(3), 319-338. "
                "https://doi.org/10.1016/0304-3932(84)90046-1\n"
                "- Fisher, I. (1930). *The theory of interest*. Macmillan. https://www.econlib.org/library/YPDBooks/Fisher/fshToI.html\n"
                "- Madura, J. (2021). *International financial management* (14th ed.). Cengage.\n"
                "- Meese, R. A., & Rogoff, K. (1983). Empirical exchange rate models of the seventies. *Journal of "
                "International Economics, 14*(1-2), 3-24. https://doi.org/10.1016/0022-1996(83)90017-X\n"
                "- Rogoff, K. (1996). The purchasing power parity puzzle. *Journal of Economic Literature, 34*(2), 647-668.\n"
                "- Taylor, A. M., & Taylor, M. P. (2004). The purchasing power parity debate. *Journal of Economic "
                "Perspectives, 18*(4), 135-158. https://doi.org/10.1257/0895330042632744\n"
                "- Bank Negara Malaysia. Exchange rates. https://www.bnm.gov.my/exchange-rates (for live inputs)")
        with st.container(border=True):
            st.subheader("Responsible-AI note")
            st.markdown("Explanations in this prototype are generated by a deterministic rule engine, not a large language "
                        "model, so every sentence is traceable to a formula. AI assistance used in building the project is "
                        "disclosed in the report.")
st.divider()
st.caption("RinggitRoute prototype · Educational use only. All preset data are illustrative.")
