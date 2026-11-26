"""
RinggitRoute - UI layer (frosted-glass theme, poster colour palette)

Pure presentation helpers: the global stylesheet and small HTML builders for the
"ruled bill" strategy scale, the tornado bars, score chips and colour-tagged notes.
No finance logic lives here; every number passed in comes from engine/fx_engine.py.
"""
from __future__ import annotations

from html import escape
from typing import Dict, List

# ---------------------------------------------------------------- poster palette
INK = "#1D2127"        # headings, dark chips
INK_SOFT = "#4A4F57"   # body text
MUTED = "#6B7078"
YELLOW = "#EECC1E"     # poster header / primary accent
YELLOW_2 = "#F2D43C"
YELLOW_3 = "#F5E17C"
CREAM = "#FCF5D4"
PAPER = "#FDFCFA"
RED = "#F45D5A"        # bill goes up / mistake
RED_SOFT = "#F7908D"
GREEN = "#0E7A3F"      # locked in / bill goes down
GREEN_SOFT = "#6FDB8E"
TAN = "#D8AC68"        # what-if band
BLUE = "#2563EB"       # forward line, Fisher link on
TRACK = "#ECE6D2"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gabarito:wght@400;500;600;700;800&display=swap');

:root {{
  --ink:{INK}; --ink-soft:{INK_SOFT}; --muted:{MUTED};
  --yellow:{YELLOW}; --yellow2:{YELLOW_2}; --yellow3:{YELLOW_3}; --cream:{CREAM}; --paper:{PAPER};
  --red:{RED}; --green:{GREEN}; --green-soft:{GREEN_SOFT}; --tan:{TAN};
  --glass: rgba(255,255,255,0.52);
  --glass-strong: rgba(255,255,255,0.70);
  --glass-edge: rgba(255,255,255,0.75);
  --glass-shadow: 0 8px 32px rgba(120, 96, 10, 0.12);
  --blur: blur(18px) saturate(160%);
}}

html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea, select, label {{
  font-family: 'Gabarito', 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
}}

/* ---- backdrop: warm poster gradient with soft colour blobs for the glass to blur ---- */
.stApp {{
  background:
    radial-gradient(900px 520px at 8% -6%, rgba(238,204,30,0.55), transparent 60%),
    radial-gradient(700px 520px at 96% 8%, rgba(245,225,124,0.65), transparent 62%),
    radial-gradient(800px 600px at 70% 105%, rgba(242,212,60,0.35), transparent 60%),
    radial-gradient(600px 420px at 20% 85%, rgba(244,93,90,0.10), transparent 60%),
    linear-gradient(160deg, #FCF5D4 0%, #FDFCFA 45%, #F8F1D8 100%);
  background-attachment: fixed;
  color: var(--ink);
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1320px; }}
h1, h2, h3, h4 {{ color: var(--ink) !important; letter-spacing: -0.01em; }}
p, li, span, label {{ color: var(--ink-soft); }}

/* ---- glass surfaces ---- */
[data-testid="stSidebar"] > div:first-child {{
  background: rgba(255,255,255,0.38);
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border-right: 1px solid var(--glass-edge);
}}
[data-testid="stSidebar"] {{ background: transparent; }}
[data-testid="stExpander"] details, [data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {{
  background: var(--glass) !important;
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-edge) !important;
  border-radius: 18px !important;
  box-shadow: var(--glass-shadow);
}}
[data-testid="stExpander"] summary p {{ font-weight: 700; color: var(--ink); }}
[data-testid="stMetric"] {{
  background: var(--glass); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-edge); border-radius: 16px; padding: .8rem 1rem; box-shadow: var(--glass-shadow);
}}
[data-testid="stMetricValue"] {{ color: var(--ink); font-weight: 800; }}
[data-testid="stMetricValue"] > div {{ font-size: 1.45rem !important; white-space: normal !important; }}

/* ---- tabs as glass pills ---- */
.stTabs [role="tablist"] {{
  gap: .35rem; background: var(--glass); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-edge) !important; border-radius: 999px; padding: .35rem; box-shadow: var(--glass-shadow);
  width: fit-content; max-width: 100%; flex-wrap: nowrap; overflow-x: auto;
}}
.stTabs [role="tablist"]::after, .stTabs [role="tablist"]::before {{ display: none !important; }}
.stTabs [data-testid="stTab"] {{
  border-radius: 999px !important; padding: .4rem .8rem !important; background: transparent; border: none !important; white-space: nowrap;
}}
.stTabs [data-testid="stTab"] p {{ font-size: .92rem; color: var(--ink); font-weight: 600; }}
.stTabs [data-testid="stTab"][aria-selected="true"] {{ background: var(--ink) !important; }}
.stTabs [data-testid="stTab"][aria-selected="true"] p {{ color: #FFFFFF !important; }}
.stTabs .react-aria-SelectionIndicator {{ display: none !important; }}
.stTabs [role="tablist"] + div, .stTabs > div > div:first-child {{ border-bottom: none !important; box-shadow: none !important; }}

/* ---- inputs ---- */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-testid="stNumberInputContainer"] {{
  background: var(--glass-strong) !important; border-radius: 12px !important;
  border-color: rgba(29,33,39,0.12) !important;
}}
input {{ color: var(--ink) !important; }}

/* ---- buttons: yellow, chunky, like the poster ---- */
.stButton > button, [data-testid="stFormSubmitButton"] > button {{
  background: var(--yellow) !important; color: var(--ink) !important; font-weight: 700 !important;
  border: none !important; border-radius: 14px !important; padding: .55rem 1.3rem !important;
  box-shadow: 0 4px 0 #C9A90E, 0 10px 24px rgba(201,169,14,0.25) !important;
  transition: transform .08s ease, box-shadow .08s ease;
}}
.stButton > button:active, [data-testid="stFormSubmitButton"] > button:active {{
  transform: translateY(3px); box-shadow: 0 1px 0 #C9A90E !important;
}}
.stButton > button p, [data-testid="stFormSubmitButton"] > button p {{ color: var(--ink) !important; font-weight: 700; }}

/* ---- radio options as pills (dark when chosen) ---- */
[data-testid="stRadio"] [role="radiogroup"] {{ gap: .45rem; flex-wrap: wrap; }}
[data-testid="stRadio"] [role="radiogroup"] > div {{ margin: 0 !important; }}
[data-testid="stRadio"] label[data-testid="stRadioOption"] {{
  background: var(--glass-strong); border: 1px solid rgba(29,33,39,0.10); border-radius: 999px;
  padding: .35rem .95rem; margin: 0 !important; box-shadow: 0 3px 0 rgba(29,33,39,0.08);
}}
[data-testid="stRadio"] label[data-testid="stRadioOption"] > div > div:first-child {{ display: none; }}
[data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked) {{ background: var(--ink); }}
[data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked) p {{ color: #FFFFFF !important; }}
[data-testid="stRadio"] label[data-testid="stRadioOption"] p {{ font-weight: 600; color: var(--ink); }}

/* ---- tables and dataframes ---- */
[data-testid="stTable"] table, [data-testid="stDataFrame"] {{ background: var(--glass-strong); border-radius: 14px; }}

/* ================= custom components ================= */
.rr-hero {{
  background: linear-gradient(120deg, rgba(238,204,30,0.92), rgba(245,225,124,0.80));
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border: 1px solid rgba(255,255,255,0.6); border-radius: 24px; padding: 1.3rem 1.6rem 1.2rem;
  box-shadow: 0 14px 40px rgba(201,169,14,0.25); margin-bottom: 1rem;
}}
.rr-kicker {{ font-size: .78rem; letter-spacing: .16em; text-transform: uppercase; font-weight: 700; color: var(--ink); opacity: .85; }}
.rr-title {{ font-size: 2.6rem; font-weight: 800; color: var(--ink); line-height: 1.05; margin: .2rem 0 .3rem; }}
.rr-tag {{ font-size: 1.12rem; font-weight: 600; color: var(--ink); }}
.rr-sub {{ font-size: .92rem; color: #3B3F45; margin-top: .25rem; }}

.rr-headline {{ display: grid; grid-template-columns: 1.1fr 1.1fr 1fr; gap: .8rem; margin: .2rem 0 1rem; }}
.rr-hcard {{
  background: var(--glass); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-edge); border-radius: 18px; padding: .85rem 1.1rem; box-shadow: var(--glass-shadow);
}}
.rr-hcard.dark {{ background: rgba(29,33,39,0.88); border-color: rgba(255,255,255,0.15); }}
.rr-hcard.dark .rr-hl, .rr-hcard.dark .rr-hv, .rr-hcard.dark .rr-hn {{ color: #FFFFFF; }}
.rr-hcard.yellow {{ background: rgba(238,204,30,0.80); }}
.rr-hl {{ font-size: .78rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 700; color: var(--ink); opacity: .8; }}
.rr-hv {{ font-size: 1.85rem; font-weight: 800; color: var(--ink); line-height: 1.1; margin: .15rem 0; }}
.rr-hn {{ font-size: .86rem; color: var(--ink-soft); }}

.rr-banner {{
  background: rgba(255,255,255,0.55); border: 1px solid rgba(244,93,90,0.35); border-left: 5px solid var(--red);
  border-radius: 12px; padding: .6rem .8rem; font-size: .88rem; color: #6B1F1D; margin-bottom: .6rem;
}}
.rr-card {{
  background: var(--glass); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--glass-edge); border-radius: 18px; padding: .95rem 1.1rem; height: 100%;
  box-shadow: var(--glass-shadow);
}}
.rr-card h4 {{ margin: 0 0 .35rem 0; font-size: 1.0rem; color: var(--ink); font-weight: 700; }}
.rr-big {{ font-size: 1.7rem; font-weight: 800; color: var(--ink); }}
.rr-small {{ font-size: .86rem; color: var(--ink-soft); }}
.rr-step {{ display:inline-block; background: var(--yellow); color: var(--ink); font-weight: 800; border-radius: 999px;
           width: 1.6rem; height: 1.6rem; text-align: center; line-height: 1.6rem; margin-right: .35rem; font-size: .85rem; }}

/* ruled bill */
.rr-bill, .rr-tor {{ width: 100%; border-collapse: collapse; border: none !important; background: transparent !important; margin: 0 !important; }}
.rr-bill th, .rr-bill td, .rr-tor th, .rr-tor td {{ border-left: none !important; border-right: none !important; border-top: none !important; background: transparent !important; }}
.rr-bill tr, .rr-tor tr {{ background: transparent !important; }}
.rr-bill th {{ font-weight: 500; color: var(--muted); font-size: .82rem; text-align: left; padding: .2rem .5rem .55rem;
              border-bottom: 2px solid rgba(29,33,39,0.12); }}
.rr-bill td {{ padding: .6rem .5rem; border-bottom: 1px solid rgba(29,33,39,0.08); vertical-align: middle; color: var(--ink); }}
.rr-bill td.s {{ font-weight: 700; width: 25%; }}
.rr-bill td.v {{ font-weight: 800; text-align: right; white-space: nowrap; width: 15%; }}
.rr-bill td.n {{ color: var(--ink-soft); font-size: .88rem; width: 24%; }}
.rr-track {{ position: relative; height: 22px; }}
.rr-track .line {{ position: absolute; left: 0; right: 0; top: 9px; height: 5px; background: {TRACK}; border-radius: 9px; }}
.rr-track .band {{ position: absolute; top: 7px; height: 9px; background: var(--tan); border-radius: 9px; opacity: .9; }}
.rr-dot {{ position: absolute; top: 2px; width: 18px; height: 18px; margin-left: -9px; border-radius: 50%; }}
.rr-dot.lock {{ background: var(--green-soft); border: 2.5px solid var(--green); }}
.rr-dot.wait {{ background: var(--ink); border: 2.5px solid var(--ink); }}
.rr-dot.naive {{ background: #FFFFFF; border: 2.5px solid #5B6168; }}
.rr-legend {{ display: flex; gap: 1.2rem; flex-wrap: wrap; font-size: .86rem; color: var(--ink-soft); margin-top: .65rem; }}
.rr-legend i {{ display:inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: .35rem; vertical-align: -1px; }}
.rr-fund {{
  margin: 1rem 0 1.1rem; background: linear-gradient(120deg, rgba(238,204,30,0.95), rgba(242,212,60,0.85));
  border-radius: 20px; padding: 1.1rem 1.4rem; display: grid; grid-template-columns: auto 1fr auto; gap: 1.4rem;
  align-items: center; box-shadow: 0 12px 30px rgba(201,169,14,0.25);
}}
.rr-fund .amt {{ font-size: 2.1rem; font-weight: 800; color: var(--ink); white-space: nowrap; }}
.rr-fund .txt {{ color: var(--ink); font-size: .95rem; }}
.rr-sticker {{
  background: var(--red); color: var(--ink); border-radius: 12px; padding: .55rem .9rem; transform: rotate(-3deg);
  box-shadow: 0 5px 0 #B83E3B; font-size: .85rem; white-space: nowrap;
}}
.rr-sticker b {{ display: block; font-size: 1.25rem; color: var(--ink); }}
.rr-sticker.ok {{ background: var(--green-soft); box-shadow: 0 5px 0 #3FA764; }}

/* predict -> reveal */
.rr-score {{ display: flex; align-items: center; gap: .55rem; margin: .4rem 0 1rem; }}
.rr-score .num {{ font-size: 2.4rem; font-weight: 800; color: var(--ink); margin-right: .4rem; }}
.rr-chip {{ width: 38px; height: 38px; border-radius: 10px; background: rgba(29,33,39,0.08); }}
.rr-chip.on {{ background: var(--green-soft); box-shadow: 0 4px 0 #3FA764; }}
.rr-qgrid {{ display: grid; grid-template-columns: 1fr 1fr; gap: .9rem; }}
.rr-q {{ background: var(--glass); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
        border: 1px solid var(--glass-edge); border-radius: 18px; padding: 1rem 1.1rem; box-shadow: var(--glass-shadow); }}
.rr-q .head {{ display: flex; justify-content: space-between; gap: .8rem; font-weight: 700; color: var(--ink); margin-bottom: .45rem; }}
.rr-pill {{ border-radius: 999px; padding: .08rem .6rem; font-size: .78rem; font-weight: 700; white-space: nowrap; height: fit-content; }}
.rr-pill.right {{ background: var(--green-soft); color: var(--ink); }}
.rr-pill.missed {{ border: 1.5px solid var(--ink); color: var(--ink); }}
.rr-q p {{ margin: .2rem 0; color: var(--ink-soft); font-size: .92rem; }}
.rr-note {{ display: flex; gap: .7rem; align-items: flex-start; margin: .45rem 0; }}
.rr-note .t {{ border-radius: 8px; padding: .12rem .55rem; font-size: .78rem; font-weight: 700; white-space: nowrap; color: var(--ink); }}
.rr-note .b {{ color: var(--ink-soft); font-size: .93rem; }}

/* checker */
.rr-result {{ border-radius: 20px; padding: 1.2rem 1.4rem; box-shadow: var(--glass-shadow); border: 1px solid rgba(255,255,255,0.6); }}
.rr-result.mistake, .rr-result.unknown {{ background: rgba(244,93,90,0.72); }}
.rr-result.acceptable {{ background: rgba(238,204,30,0.80); }}
.rr-result.correct {{ background: rgba(111,219,142,0.85); }}
.rr-result .lab {{ display: inline-block; background: var(--ink); color: #FFFFFF; border-radius: 999px; padding: .12rem .65rem;
                  font-size: .78rem; font-weight: 700; margin-bottom: .6rem; }}
.rr-result .msg {{ color: var(--ink); font-size: 1.0rem; }}
.rr-result .vl {{ color: var(--ink); font-size: .82rem; margin-top: .9rem; }}
.rr-result .vv {{ color: var(--ink); font-size: 1.6rem; font-weight: 800; }}
.rr-try {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin-bottom: 1.2rem; }}
.rr-try div {{ border-radius: 16px; padding: .9rem 1rem; color: var(--ink); box-shadow: 0 5px 0 rgba(29,33,39,0.12); }}
.rr-try div b {{ display: block; font-size: 1.35rem; color: var(--ink); margin-bottom: .3rem; }}
.rr-try div span {{ font-size: .85rem; color: var(--ink); }}
.rr-try .r {{ background: var(--red); transform: rotate(-2deg); }}
.rr-try .y {{ background: var(--yellow); transform: rotate(1deg); }}
.rr-try .g {{ background: var(--green-soft); transform: rotate(-1deg); }}

/* tornado */

.rr-tor th {{ font-weight: 500; color: var(--muted); font-size: .82rem; text-align: left; padding: .2rem .4rem .5rem;
             border-bottom: 2px solid rgba(29,33,39,0.12); }}
.rr-tor td {{ padding: .55rem .4rem; border-bottom: 1px solid rgba(29,33,39,0.08); vertical-align: middle; }}
.rr-tor td.in {{ font-weight: 700; color: var(--ink); width: 20%; }}
.rr-tor .row {{ display: grid; grid-template-columns: 2.6rem 1fr 5.6rem; gap: .5rem; align-items: center; margin: .15rem 0; }}
.rr-tor .pp {{ font-size: .8rem; color: var(--muted); }}
.rr-tor .bar {{ position: relative; height: 12px; background: {TRACK}; border-radius: 9px; }}
.rr-tor .bar .mid {{ position: absolute; left: 50%; top: -4px; bottom: -4px; width: 2px; background: #C8BE9C; }}
.rr-tor .bar .fill {{ position: absolute; top: 0; bottom: 0; border-radius: 9px; }}
.rr-tor .val {{ text-align: right; font-weight: 800; font-size: .88rem; color: var(--ink); font-variant-numeric: tabular-nums; }}
.rr-running {{ display: inline-block; background: var(--ink); color: #FFFFFF; border-radius: 12px; padding: .5rem .9rem;
              font-weight: 700; margin: .3rem 0 .6rem; }}
.rr-running span {{ color: var(--yellow); }}
[data-testid="stAlert"] {{ background: rgba(245,225,124,0.45) !important; border: 1px solid rgba(238,204,30,0.6); border-radius: 14px; }}
[data-testid="stAlert"] p {{ color: var(--ink) !important; }}
footer {{ visibility: hidden; }}
</style>
"""

NOTE_TAGS = {
    "Inflation": YELLOW_3,
    "Interest": "#BFD4FF",
    "Fisher": "#D9CCFF",
    "Budget": RED_SOFT,
    "No free lunch": GREEN_SOFT,
}


def rm(x: float) -> str:
    return f"RM {x:,.2f}"


def headline(forward_cost: float, set_aside: float, gap: float, months: int, i_home: float) -> str:
    gap_word = "short by" if gap > 0 else "over by"
    return f"""
<div class="rr-headline">
  <div class="rr-hcard dark"><div class="rr-hl">Forward-locked cost</div><div class="rr-hv">{rm(forward_cost)}</div>
    <div class="rr-hn">paid in month {months}, rate fixed today</div></div>
  <div class="rr-hcard yellow"><div class="rr-hl">Set aside today</div><div class="rr-hv">{rm(set_aside)}</div>
    <div class="rr-hn">in a ringgit deposit at {i_home*100:.2f}%</div></div>
  <div class="rr-hcard"><div class="rr-hl">Naive budget {gap_word}</div><div class="rr-hv">{rm(abs(gap))}</div>
    <div class="rr-hn">today's rate &times; today's prices</div></div>
</div>"""


def ruled_bill(rows: List[Dict], band: tuple, deviation: float) -> str:
    """rows: dicts with label, value, kind (lock|wait|naive), note, band (bool)."""
    lo = min([r["value"] for r in rows] + [band[0]])
    hi = max([r["value"] for r in rows] + [band[1]])
    span = (hi - lo) or 1.0

    def pos(v):
        return 3 + 94 * (v - lo) / span

    body = []
    for r in rows:
        band_html = ""
        if r.get("band"):
            band_html = f'<div class="band" style="left:{pos(band[0]):.2f}%;width:{pos(band[1]) - pos(band[0]):.2f}%"></div>'
        body.append(
            f'<tr><td class="s">{escape(r["label"])}</td><td class="v">{rm(r["value"])}</td>'
            f'<td><div class="rr-track"><div class="line"></div>{band_html}'
            f'<div class="rr-dot {r["kind"]}" style="left:{pos(r["value"]):.2f}%"></div></div></td>'
            f'<td class="n">{escape(r["note"])}</td></tr>')
    return f"""
<table class="rr-bill">
  <tr><th>Strategy</th><th style="text-align:right">Ringgit cost at payment date</th>
      <th><span style="float:left">{rm(lo)}</span><span style="float:right">{rm(hi)}</span></th><th>Note</th></tr>
  {''.join(body)}
</table>
<div class="rr-legend">
  <span><i style="background:{GREEN}"></i>locked in today</span>
  <span><i style="background:{INK}"></i>wait and convert later</span>
  <span><i style="background:#fff;border:2px solid #5B6168"></i>naive budget</span>
  <span><i style="background:{TAN};border-radius:6px;width:22px"></i>your &plusmn;{deviation*100:.1f}% what-if range</span>
</div>
<div class="rr-small" style="margin-top:.35rem">The scale runs from the lowest to the highest cost, not from zero.</div>"""


def fund_band(set_aside: float, i_home: float, gap: float) -> str:
    if gap > 0.005:
        sticker = f'<div class="rr-sticker">The naive budget is short by<b>{rm(gap)}</b></div>'
    else:
        sticker = f'<div class="rr-sticker ok">The naive budget covers it, with<b>{rm(-gap)}</b> spare</div>'
    return f"""
<div class="rr-fund"><div class="amt">{rm(set_aside)}</div>
  <div class="txt">To fund the forward-locked plan, set aside this amount today in a ringgit deposit at {i_home*100:.2f}%.</div>
  {sticker}</div>"""


def score_row(score: int, oks: List[bool]) -> str:
    chips = "".join(f'<div class="rr-chip{" on" if ok else ""}"></div>' for ok in oks)
    return f'<div class="rr-score"><span class="num">{score} / {len(oks)}</span>{chips}<span class="rr-small">Score</span></div>'


def question_cards(feedback: List[Dict]) -> str:
    cards = []
    for f in feedback:
        pill = '<span class="rr-pill right">Right</span>' if f["ok"] else '<span class="rr-pill missed">Missed</span>'
        cards.append(
            f'<div class="rr-q"><div class="head"><span>{escape(f["question"])}</span>{pill}</div>'
            f'<p>Correct answer: <b>{escape(f["correct"])}</b></p><p>{escape(f["why"])}</p></div>')
    return f'<div class="rr-qgrid">{"".join(cards)}</div>'


def tagged_notes(lines: List[str]) -> str:
    out = []
    for line in lines:
        tag, _, text = line.partition(":")
        colour = NOTE_TAGS.get(tag.strip(), "#E5E7EB")
        out.append(f'<div class="rr-note"><span class="t" style="background:{colour}">{escape(tag.strip())}</span>'
                   f'<span class="b">{escape(text.strip())}</span></div>')
    return "".join(out)


def result_card(status: str, message: str, verified: str) -> str:
    label = {"correct": "Correct", "acceptable": "Acceptable with a note",
             "mistake": "Known mistake detected", "unknown": "Does not match"}[status]
    return (f'<div class="rr-result {status}"><span class="lab">{label}</span><div class="msg">{escape(message)}</div>'
            f'<div class="vl">Verified value</div><div class="vv">{escape(verified)}</div></div>')


def try_cards(inverted: float, approx_real: float, correct: float) -> str:
    return f"""
<div class="rr-try">
  <div class="r"><b>{inverted:.4f}</b><span>as the forward rate (a classic inverted-ratio slip).</span></div>
  <div class="y"><b>{approx_real:.2f}</b><span>as the real rate (the i &minus; &pi; shortcut).</span></div>
  <div class="g"><b>{correct:.4f}</b><span>to see a correct answer.</span></div>
</div>"""


def tornado_bars(rows: List[Dict]) -> str:
    maxabs = max([abs(r[k]) for r in rows for k in ("fwd_down", "fwd_up", "ppp_down", "ppp_up")] + [1e-9])

    def bar(v):
        w = 50 * abs(v) / maxabs
        colour = RED if v > 0.005 else GREEN
        left = 50 if v > 0 else 50 - w
        fill = f'<div class="fill" style="left:{left:.2f}%;width:{w:.2f}%;background:{colour}"></div>' if abs(v) > 0.005 else ""
        return f'<div class="bar">{fill}<div class="mid"></div></div>'

    def pair(down, up):
        return (f'<div class="row"><span class="pp">&minus;1 pp</span>{bar(down)}<span class="val">{down:+,.2f}</span></div>'
                f'<div class="row"><span class="pp">+1 pp</span>{bar(up)}<span class="val">{up:+,.2f}</span></div>')

    body = "".join(
        f'<tr><td class="in">{escape(r["input"])}</td><td>{pair(r["fwd_down"], r["fwd_up"])}</td>'
        f'<td>{pair(r["ppp_down"], r["ppp_up"])}</td></tr>' for r in rows)
    return f"""
<table class="rr-tor">
  <tr><th>Input</th><th>Forward cost (RM change)</th><th>PPP cost (RM change)</th></tr>
  {body}
</table>
<div class="rr-legend"><span><i style="background:{RED}"></i>bill goes up</span>
<span><i style="background:{GREEN}"></i>bill goes down</span></div>"""
