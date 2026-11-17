"""Design tokens dan style global dashboard."""

from __future__ import annotations

import streamlit as st


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --ink: #1e293b;
  --muted: #64748b;
  --faint: #94a3b8;
  --line: #e5eaf1;
  --canvas: #f7f9fc;
  --surface: #ffffff;
  --blue: #2f6be4;
  --blue-soft: #edf3ff;
  --teal: #0f8a7e;
  --teal-soft: #e9f7f4;
  --amber: #b7791f;
  --amber-soft: #fff7e8;
  --red: #c24d4d;
  --red-soft: #fdf0f0;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background: var(--canvas); }
[data-testid="stHeader"] { background: transparent; }
/* Toolbar bawaan disamarkan, TAPI tombol buka/tutup sidebar tetap terlihat */
[data-testid="stToolbarActions"], [data-testid="stDeployButton"] { display: none; }
[data-testid="stSidebarCollapsedControl"] { display: flex !important; visibility: visible !important; }
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button { background: #fff !important; border: 1px solid var(--line) !important; border-radius: 8px !important; box-shadow: 0 2px 8px rgba(30,41,59,.08) !important; }
[data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); min-width: 258px; }
[data-testid="stSidebar"] * { color: var(--ink); }
[data-testid="stSidebar"] .stRadio > label { color: var(--faint); font-size: .64rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; padding-left: .25rem; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] { gap: .18rem; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label { position: relative; padding: .58rem .72rem !important; border-radius: 8px; transition: background .15s ease; }
/* Sembunyikan kontrol radio Streamlit, tetapi biarkan seluruh baris menu tetap dapat diklik. */
[data-testid="stSidebar"] .stRadio [role="radiogroup"] input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label > div:first-child,
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label > label:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label > div:last-child { margin-left: 0 !important; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover { background: #f2f6fc; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) { background: var(--blue-soft); }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) p { color: var(--blue); font-weight: 700; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label p { font-size: .86rem; }
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label [data-testid="stMarkdownContainer"] p { margin: 0; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--muted); }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #fbfcfe; border-color: #dfe6ef; min-height: 2.35rem; }
[data-testid="stSidebar"] [data-baseweb="select"] span { color: var(--ink); font-size: .84rem; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: .7rem; font-weight: 600; color: #64748b; }
[data-testid="stSidebar"] .stButton button { border: 1px solid #cbd8e8; background: #fff; color: #40516a; border-radius: 8px; font-size: .82rem; font-weight: 600; min-height: 2.35rem; text-align: left; justify-content: flex-start; padding-left: .9rem; box-shadow: 0 1px 2px rgba(37,76,125,.04); }
[data-testid="stSidebar"] .stButton button:hover { border-color: #79a5e6; color: #2459b8; background: #f4f8ff; }
[data-testid="stSidebar"] .stButton button[kind="primary"] { border-color: #2f6be4; color: #174ea6; background: #edf3ff; font-weight: 700; box-shadow: 0 2px 7px rgba(47,107,228,.12); }
[data-testid="stSidebar"] .stButton button[kind="primary"] p { color: #174ea6; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] { background: var(--blue-soft); color: var(--blue); border-radius: 6px; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span { color: var(--blue); }

.block-container { max-width: 1560px; padding: 2.1rem 2.9rem 3.4rem; }
h1, h2, h3, h4 { color: var(--ink); font-family: 'Space Grotesk', sans-serif; letter-spacing: -.025em; }
h1 { font-size: clamp(1.7rem, 2.7vw, 2.35rem); margin: .15rem 0 .35rem; }
h2 { font-size: 1.3rem; margin-top: .2rem; }
h3 { font-size: 1.02rem; }
p, li { color: var(--muted); }
hr { border-color: var(--line); margin: 1.1rem 0; }

.brand-mark { display: flex; gap: .7rem; align-items: center; margin: .3rem 0 1.7rem; padding: .2rem 0 .9rem; border-bottom: 1px solid var(--line); }
.brand-wordmark { border-left: 3px solid var(--blue); padding-left: .65rem; }
.brand-name { color: #172b4d; font: 700 .96rem 'Space Grotesk', sans-serif; line-height: 1.2; }
.brand-sub { color: #64748b; font-size: .64rem; letter-spacing: .04em; text-transform: uppercase; margin-top: .2rem; }
.side-label { color: #7b8798; font-size: .62rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: .7rem 0 .35rem .35rem; }
.side-label-spaced { margin-top: 1.05rem; }
.sidebar-spacer { height: 1.5rem; }
.side-rule { border-top: 1px solid var(--line); margin: .7rem 0 .85rem; }
.user-chip { display: flex; align-items: center; gap: .6rem; padding: .65rem .55rem; background: #fff; border: 0; border-radius: 0; margin: .2rem 0 .35rem; }
.user-avatar { width: 32px; height: 32px; display: grid; place-items: center; border-radius: 50%; background: #e8edf5; color: #42536b; font-weight: 700; font-size: .7rem; }
.user-name { color: var(--ink); font-weight: 600; font-size: .8rem; }
.user-role { color: var(--faint); font-size: .65rem; }

.eyebrow { color: var(--blue); font-size: .68rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; margin-bottom: .25rem; }
.hero-band { background: linear-gradient(115deg, #fff 0%, #f8fbff 100%); border: 1px solid #dce5f1; border-radius: 14px; padding: 1.2rem 1.4rem; display: flex; justify-content: space-between; align-items: flex-start; gap: 1.2rem; margin-bottom: .95rem; box-shadow: 0 5px 18px rgba(23,43,77,.035); }
.hero-band > div:first-child { flex: 1 1 auto; min-width: 0; }
.hero-band h1 { font-size: clamp(1.25rem, 2vw, 1.55rem); margin: 0 0 .2rem; line-height: 1.22; }
.hero-band p { margin: 0; font-size: .8rem; }
.hero-band .header-chips { flex: 0 0 auto; padding-top: .15rem; }
.hero-id { color: var(--blue); font-size: .58rem; font-weight: 700; letter-spacing: .06em; margin-right: .5rem; }
.header-chips { display: flex; flex-wrap: wrap; gap: .35rem; justify-content: flex-end; }
.header-chip { background: #f8fafc; border: 1px solid #e7ecf3; border-radius: 6px; color: #475569; font-size: .68rem; font-weight: 600; padding: .32rem .55rem; white-space: nowrap; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: #18a07f; display: inline-block; margin-right: .3rem; }

.st-key-filter_panel { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: .78rem 1rem .65rem; margin-bottom: .9rem; }
.filter-title { color: var(--faint); font-size: .6rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 0 0 .15rem; }
.st-key-filter_panel [data-testid="stWidgetLabel"] p { color: #64748b; font-size: .68rem; font-weight: 600; }
.st-key-filter_panel [data-baseweb="select"] > div { background: #fbfcfe; border-color: #e2e8f0; min-height: 2.25rem; }
.st-key-filter_panel [data-baseweb="select"] span { font-size: .8rem; color: var(--ink); }
.st-key-filter_panel .stButton button { border: 1px solid #dce5f1; color: #475569; font-size: .76rem; min-height: 2.2rem; background: #fff; }
.st-key-filter_panel [data-testid="stMultiSelect"] [data-baseweb="tag"] { background: var(--blue-soft); }
.st-key-trend_card, .st-key-comparison_card, .st-key-cluster_chart_card, .st-key-jisdor_chart_card, .st-key-map_card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: .95rem 1rem .55rem; }
.st-key-trend_card .section-head, .st-key-comparison_card .section-head, .st-key-map_card .section-head { margin-top: 0; }
.st-key-trend_card .section-note, .st-key-comparison_card .section-note { max-width: 42ch; }
.st-key-map_card { margin-bottom: .9rem; }

.kpi-card { background: linear-gradient(145deg, #fff 0%, #fbfcff 100%); border: 1px solid #d8e1ed; border-radius: 13px; padding: .9rem .95rem .85rem 1.05rem; min-height: 116px; position: relative; overflow: hidden; transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease; box-shadow: 0 3px 10px rgba(23,43,77,.045); }
.kpi-card:hover { transform: translateY(-2px); border-color: #b8c9df; box-shadow: 0 10px 24px rgba(30,55,90,.10); }
.kpi-card::after { content: ''; position: absolute; left: 0; top: .75rem; bottom: .75rem; width: 4px; border-radius: 0 4px 4px 0; background: var(--accent, var(--blue)); }
.kpi-head { display: flex; justify-content: space-between; align-items: center; }
.kpi-label { color: #475569; font-size: .72rem; font-weight: 700; }
.kpi-value { color: #172b4d; font: 700 1.3rem 'Space Grotesk', sans-serif; letter-spacing: -.035em; margin: .55rem 0 .4rem; white-space: nowrap; }
.kpi-value small { color: #64748b; font: 600 .67rem 'DM Sans', sans-serif; letter-spacing: 0; margin-left: .1rem; }
.kpi-note { color: #64748b; font-size: .64rem; display: flex; align-items: center; gap: .35rem; min-width: 0; }
.kpi-detail { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kpi-icon { color: var(--accent, var(--blue)); background: #f1f5fd; border: 1px solid #e4eaf4; border-radius: 8px; width: 27px; height: 27px; display: grid; place-items: center; font-size: .76rem; font-weight: 700; }
.kpi-badge { border-radius: 999px; padding: .13rem .38rem; font-size: .58rem; font-weight: 700; letter-spacing: .02em; flex: 0 0 auto; }
.badge-warm { background: var(--amber-soft); color: var(--amber); }
.badge-cool { background: var(--blue-soft); color: var(--blue); }
.badge-safe { background: var(--teal-soft); color: var(--teal); }

.section-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; margin: 1.45rem 0 .5rem; }
.section-title { color: var(--ink); font: 600 1.08rem 'Space Grotesk', sans-serif; margin: 0; display: flex; align-items: center; gap: .45rem; }
.section-title::before { content: ''; width: 8px; height: 8px; background: var(--blue); display: inline-block; border-radius: 2px; }
.section-note { color: #94a3b8; font-size: .71rem; margin: .18rem 0 0; }
.section-chip { color: #64748b; background: #fff; border: 1px solid #e6ebf2; border-radius: 5px; padding: .25rem .5rem; font-size: .65rem; font-weight: 600; white-space: nowrap; }
.surface { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: .9rem 1rem .55rem; }
.surface-title { color: var(--ink); font-size: .84rem; font-weight: 700; margin: 0 0 .12rem; }
.surface-note { color: #94a3b8; font-size: .68rem; margin: 0 0 .4rem; }

.callout { background: #f7faff; border: 1px solid #e1ebfa; border-radius: 8px; padding: .68rem .85rem; color: #58708f; font-size: .71rem; line-height: 1.5; }
.empty-state { text-align: center; background: #fff; border: 1px dashed #cad3e0; border-radius: 11px; padding: 2.1rem 1rem; color: var(--muted); font-size: .8rem; }
.empty-icon { font-size: 1.35rem; margin-bottom: .4rem; }

.cluster-table-wrap { background: #fff; border: 1px solid var(--line); border-radius: 11px; padding: .85rem .95rem .55rem; }
.cluster-table { width: 100%; border-collapse: collapse; font-size: .74rem; }
.cluster-table th { color: #8493a8; font-size: .58rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; text-align: left; padding: .35rem .45rem; border-bottom: 1px solid var(--line); }
.cluster-table td { color: #475569; padding: .58rem .45rem; border-bottom: 1px solid #f0f3f8; vertical-align: middle; }
.cluster-table tr:last-child td { border-bottom: 0; }
.cluster-table td b { color: var(--ink); font-size: .75rem; }
.cluster-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); display: inline-block; margin-right: .4rem; }
.table-note { color: #94a3b8; font-size: .61rem; font-style: italic; margin: .65rem 0 .2rem; }

.insight-card { background: #fff; border: 1px solid var(--line); border-radius: 11px; padding: .85rem .9rem .7rem; min-height: 190px; }
.insight-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: .55rem; }
.cluster-badge { color: var(--accent, var(--blue)); background: #f4f7fd; border-radius: 5px; padding: .18rem .42rem; font-size: .61rem; font-weight: 700; }
.insight-members { color: #94a3b8; font-size: .62rem; }
.insight-metric { display: flex; justify-content: space-between; border-bottom: 1px solid #f1f4f8; padding: .2rem 0; font-size: .67rem; color: #94a3b8; }
.insight-metric strong { color: var(--ink); font-size: .71rem; }
.insight-label { color: #8493a8; font-size: .57rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; margin: .6rem 0 .2rem; }
.insight-card p { font-size: .69rem; line-height: 1.5; margin: 0; }
.insight-members-list { color: #64748b !important; }

.jisdor-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: .8rem; }
.jisdor-panel { background: #fff; border: 1px solid var(--line); border-radius: 11px; padding: 1rem 1.05rem; display: flex; align-items: center; gap: .85rem; }
.jisdor-icon { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 8px; background: var(--blue-soft); color: var(--blue); font-weight: 700; }
.jisdor-label { color: #8493a8; font-size: .56rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.jisdor-value { color: var(--ink); font: 700 1.12rem 'Space Grotesk', sans-serif; margin: .15rem 0; }
.jisdor-value small { color: #94a3b8; font: 500 .68rem 'DM Sans', sans-serif; }
.jisdor-date { color: #94a3b8; font-size: .65rem; }
.jisdor-callout { align-self: stretch; display: flex; align-items: center; }

.trend-foot, .comparison-foot { display: flex; justify-content: space-between; gap: .55rem; border-top: 1px solid #f0f3f8; margin-top: .25rem; padding-top: .6rem; color: #94a3b8; font-size: .64rem; }
.trend-foot b, .comparison-foot b { color: var(--ink); font-weight: 700; margin-left: .22rem; }
.comparison-foot div { display: flex; flex-direction: column; gap: .14rem; }
.comparison-foot span { font-size: .58rem; text-transform: uppercase; letter-spacing: .04em; }
.cluster-legend { display: flex; flex-wrap: wrap; gap: .7rem; padding-bottom: .3rem; }
.cluster-legend span { color: #64748b; font-size: .68rem; display: flex; align-items: center; gap: .3rem; }
.cluster-legend i { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.metric-strip { display: flex; flex-wrap: wrap; gap: .5rem; background: #fff; border: 1px solid var(--line); border-radius: 9px; padding: .55rem .7rem; margin-top: .55rem; color: #8493a8; font-size: .65rem; }
.metric-strip b { color: var(--ink); margin-left: .25rem; }
.sidebar-note { background: #f8fafd; border: 1px solid #eef2f7; border-radius: 9px; padding: .7rem .8rem; }
.sidebar-note-title { color: #475569; font-size: .66rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; margin-bottom: .3rem; }
.sidebar-note p { color: #94a3b8; font-size: .65rem; line-height: 1.45; margin: .12rem 0; }
.app-footer { display: flex; justify-content: space-between; gap: 1rem; border-top: 1px solid var(--line); margin-top: 1.9rem; padding-top: .85rem; color: #9aa7b8; font-size: .64rem; }

.login-shell { max-width: 460px; margin: 8vh auto 0; }
.login-brand { text-align: center; margin-bottom: 1.55rem; }
.login-brand .eyebrow { margin-bottom: .55rem; }
.login-brand h1 { font-size: clamp(1.7rem, 3vw, 2.1rem); }
.login-brand p { margin: .35rem 0; font-size: .88rem; }
.login-meta { max-width: 470px; margin: 1.25rem auto 0; text-align: center; border-top: 1px solid #d7e0eb; padding-top: .85rem; font-size: .72rem; color: #64748b; }
[data-testid="stForm"] { background: #fff; border: 1px solid #cbd7e5; border-radius: 16px; padding: 1.5rem 1.45rem 1.4rem; box-shadow: 0 20px 48px rgba(23,43,77,.13), 0 3px 10px rgba(23,43,77,.05); max-width: 470px; margin: 0 auto; }
[data-testid="stForm"] [data-testid="stWidgetLabel"] p { color: #334155; font-size: .76rem; font-weight: 700; }
[data-testid="stForm"] [data-baseweb="input"] { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 9px; transition: border-color .15s ease, box-shadow .15s ease; }
[data-testid="stForm"] [data-baseweb="input"]:focus-within { background: #fff; border-color: var(--blue); box-shadow: 0 0 0 3px rgba(47,107,228,.1); }
[data-testid="stForm"] input { background: transparent; padding: .5rem .7rem; font-size: .84rem; }
.stButton button, [data-testid="stFormSubmitButton"] button { border-radius: 8px; font-weight: 700; min-height: 2.4rem; }
[data-testid="stFormSubmitButton"] button { background: var(--blue) !important; border-color: var(--blue) !important; min-height: 2.75rem; }
[data-testid="stFormSubmitButton"] button, [data-testid="stFormSubmitButton"] button p, [data-testid="stFormSubmitButton"] button div { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
[data-testid="stFormSubmitButton"] button:hover { background: #2459c9 !important; border-color: #2459c9 !important; }

@media (max-width: 1100px) {
  .block-container { padding: 1.4rem 1.2rem 3rem; }
  .hero-band { flex-direction: column; align-items: flex-start; }
  .jisdor-grid { grid-template-columns: 1fr; }
}
@media (max-width: 800px) {
  .app-footer { flex-direction: column; gap: .35rem; }
  .section-head { align-items: flex-start; flex-direction: column; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
"""


def inject_global_styles() -> None:
    """Memasang stylesheet global pada aplikasi Streamlit."""

    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
