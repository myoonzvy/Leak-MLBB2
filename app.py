import html
import json
from pathlib import Path

import streamlit as st

BASE_URL = "https://survey.moontontech.net/t/5RVO"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RESULTS_FILE = Path("results.json")

st.set_page_config(
    page_title="5RVO Survey Link Scanner",
    page_icon="🔎",
    layout="wide",
)

st.markdown(
    """
<style>
:root {
    --bg: #010001;
    --panel: #10191d;
    --panel-2: #133336;
    --teal: #367D8A;
    --teal-dark: #285F6B;
    --text: #FFFFFF;
    --muted: #7d8a99;
    --green-bg: #0d3026;
    --green-border: #1d7a52;
    --green-text: #4ade80;
    --red-bg: #2b141b;
    --red-border: #6f2635;
    --red-text: #d55b6a;
    --orange: #f97316;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg);
}

[data-testid="stHeader"] {
    background: rgba(1, 0, 1, 0.78);
}

.block-container {
    padding-top: 2.2rem;
    max-width: 1180px;
}

.hero {
    border-bottom: 1px solid rgba(54, 125, 138, 0.35);
    padding-bottom: 1.2rem;
    margin-bottom: 1.5rem;
}

.hero-kicker {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    color: var(--teal);
    letter-spacing: .22em;
    font-size: .72rem;
    text-transform: uppercase;
    margin-bottom: .6rem;
}

.hero-title {
    font-family: Georgia, 'Times New Roman', serif;
    color: var(--text);
    font-size: clamp(2.1rem, 8vw, 4.8rem);
    line-height: .92;
    font-weight: 400;
    letter-spacing: -.045em;
    margin: 0;
}

.hero-subtitle {
    color: var(--muted);
    margin-top: .9rem;
    font-size: .95rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .7rem;
    margin: 1rem 0 1.5rem;
}

.stat-card {
    background: linear-gradient(180deg, rgba(19, 51, 54, .72), rgba(16, 25, 29, .92));
    border: 1px solid rgba(54, 125, 138, .35);
    border-radius: 18px;
    padding: 1rem;
}

.stat-label {
    color: var(--muted);
    font-size: .72rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.stat-value {
    color: var(--text);
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 2.35rem;
    line-height: 1;
    margin-top: .35rem;
    font-weight: 400;
}

.section-label {
    display: flex;
    align-items: center;
    gap: .7rem;
    color: var(--muted);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    text-transform: uppercase;
    letter-spacing: .20em;
    font-size: .74rem;
    font-weight: 600;
    margin: 1.2rem 0 .85rem;
}

.section-label::before {
    content: '';
    width: 5px;
    height: 22px;
    border-radius: 99px;
    background: var(--orange);
}

.prefix-card {
    background: rgba(16, 25, 29, .94);
    border: 1px solid rgba(54, 125, 138, .35);
    border-radius: 18px;
    margin: .85rem 0;
    overflow: hidden;
}

.prefix-card summary {
    list-style: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: .75rem;
    padding: 1rem 1.05rem;
    color: var(--text);
    font-size: 1.05rem;
    font-weight: 400;
}

.prefix-card summary::-webkit-details-marker {
    display: none;
}

.prefix-card summary::after {
    content: '▾';
    margin-left: auto;
    color: var(--muted);
    font-size: .75rem;
}

.badge {
    border-radius: 999px;
    padding: .18rem .65rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: .84rem;
    font-weight: 600;
    background: rgba(249, 115, 22, .16);
    color: #ff9b50;
    border: 1px solid rgba(249, 115, 22, .38);
}

.prefix-name {
    font-size: 1.18rem;
    font-weight: 400;
}

.prefix-meta {
    color: var(--muted);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: .92rem;
    font-weight: 400;
}

.link-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
    gap: .55rem;
    padding: 0 1.05rem 1.05rem;
}

.link-tile {
    display: block;
    text-align: center;
    padding: .68rem .45rem;
    border-radius: 10px;
    text-decoration: none !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: .95rem;
    font-weight: 500;
    transition: transform .12s ease, border-color .12s ease, background .12s ease;
}

.link-tile:hover {
    transform: translateY(-1px);
}

.link-working {
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    color: var(--green-text) !important;
}

.link-dead {
    background: var(--red-bg);
    border: 1px solid var(--red-border);
    color: var(--red-text) !important;
    opacity: .88;
    pointer-events: none;
}

.empty-note {
    color: var(--muted);
    padding: 0 1.05rem 1.05rem;
    font-size: .9rem;
}

[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div,
[data-testid="stRadio"] label {
    font-weight: 400 !important;
}

@media (max-width: 640px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stats-grid {
        grid-template-columns: 1fr;
    }
    .link-grid {
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: .45rem;
    }
    .link-tile {
        font-size: .88rem;
        padding: .62rem .25rem;
    }
    .prefix-card summary {
        gap: .55rem;
        padding: .85rem;
    }
    .prefix-meta {
        display: none;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

if not RESULTS_FILE.exists():
    st.error("results.json not found. Run scan.py first or wait for GitHub Actions to generate it.")
    st.stop()

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

total_links = len(ALPHABET) * len(ALPHABET)
working_links = 0
groups = []

for first in ALPHABET:
    row = results.get(first, {})
    working = []
    dead = []

    for second in ALPHABET:
        status = row.get(second)
        if status == 200:
            working.append(second)
            working_links += 1
        else:
            dead.append(second)

    groups.append({
        "prefix": first,
        "working": working,
        "dead": dead,
        "count": len(working),
    })

dead_links = total_links - working_links

st.markdown(
    f"""
<div class="hero">
  <div class="hero-kicker">Survey Link Viewer</div>
  <h1 class="hero-title">5RVO Survey<br>Scanner</h1>
  <div class="hero-subtitle">Active and inactive survey links, grouped by prefix.</div>
</div>
<div class="stats-grid">
  <div class="stat-card"><div class="stat-label">Total Checked</div><div class="stat-value">{total_links}</div></div>
  <div class="stat-card"><div class="stat-label">Working</div><div class="stat-value">{working_links}</div></div>
  <div class="stat-card"><div class="stat-label">Dead / Unknown</div><div class="stat-value">{dead_links}</div></div>
</div>
""",
    unsafe_allow_html=True,
)

search = st.text_input("Search code", placeholder="Example: Oa, O9, OV")

show_mode = st.radio(
    "Show",
    ["Working only", "All links"],
    horizontal=True,
)

sort_mode = st.selectbox(
    "Sort prefixes",
    ["Partial first", "Most working first", "A-Z"],
)

if sort_mode == "Most working first":
    groups.sort(key=lambda x: x["count"], reverse=True)
elif sort_mode == "Partial first":
    groups.sort(
        key=lambda x: (
            not (0 < x["count"] < len(ALPHABET)),
            -x["count"],
            x["prefix"],
        )
    )
else:
    groups.sort(key=lambda x: x["prefix"])

section_title = "Partial Prefixes — Expanded" if sort_mode == "Partial first" else "Prefixes"
st.markdown(f'<div class="section-label">{section_title}</div>', unsafe_allow_html=True)

for group in groups:
    prefix = group["prefix"]
    working = group["working"]

    if show_mode == "Working only" and not working:
        continue

    expanded = " open" if 0 < len(working) < len(ALPHABET) else ""
    tiles = []

    for second in ALPHABET:
        code = prefix + second
        is_working = second in working

        if show_mode == "Working only" and not is_working:
            continue
        if search and search.lower() not in code.lower():
            continue

        safe_code = html.escape(code)
        if is_working:
            safe_url = html.escape(BASE_URL + code, quote=True)
            tiles.append(f'<a class="link-tile link-working" href="{safe_url}" target="_blank" rel="noopener">{safe_code}</a>')
        else:
            tiles.append(f'<span class="link-tile link-dead">{safe_code}</span>')

    if not tiles:
        body = '<div class="empty-note">No matching links.</div>'
    else:
        body = '<div class="link-grid">' + ''.join(tiles) + '</div>'

    card_html = f"""
<details class="prefix-card"{expanded}>
  <summary>
    <span class="badge">{len(working)}/62</span>
    <span class="prefix-name">Prefix {html.escape(prefix)}</span>
    <span class="prefix-meta">{len(working)} working / {62 - len(working)} dead</span>
  </summary>
  {body}
</details>
"""
    st.markdown(card_html, unsafe_allow_html=True)
