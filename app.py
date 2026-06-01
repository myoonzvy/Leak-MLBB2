import json
from pathlib import Path

import streamlit as st

BASE_URL = "https://survey.moontontech.net/t/5RVO"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RESULTS_FILE = Path("results.json")

st.set_page_config(
    page_title="5RV4 Survey Link Scanner",
    page_icon="🔎",
    layout="wide",
)

st.title("5RV4 Survey Link Scanner")
st.caption("Streamlit viewer for scanned 5RV4 survey links.")

if not RESULTS_FILE.exists():
    st.error("results.json not found. Run scan.py first or wait for GitHub Actions to generate it.")
    st.stop()

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

total_links = len(ALPHABET) * len(ALPHABET)
working_links = 0
dead_links = 0

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
            dead_links += 1

    groups.append({
        "prefix": first,
        "working": working,
        "dead": dead,
        "count": len(working),
    })

col1, col2, col3 = st.columns(3)
col1.metric("Total Checked", total_links)
col2.metric("Working", working_links)
col3.metric("Dead / Unknown", dead_links)

st.divider()

search = st.text_input("Search code", placeholder="Example: aB, Z9, m")

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

for group in groups:
    prefix = group["prefix"]
    working = group["working"]
    dead = group["dead"]

    if show_mode == "Working only" and not working:
        continue

    title = f"Prefix {prefix} — {len(working)}/62 working"

    with st.expander(title, expanded=(0 < len(working) < 62)):
        codes = []

        if show_mode == "Working only":
            for second in working:
                codes.append((second, True))
        else:
            for second in ALPHABET:
                codes.append((second, second in working))

        filtered_codes = []

        for second, is_working in codes:
            code = prefix + second

            if search and search.lower() not in code.lower():
                continue

            filtered_codes.append((code, is_working))

        if not filtered_codes:
            st.caption("No matching links.")
            continue

        cols = st.columns(6)

        for i, (code, is_working) in enumerate(filtered_codes):
            url = BASE_URL + code

            with cols[i % 6]:
                if is_working:
                    st.link_button(code, url)
                else:
                    st.button(f"{code} ✕", disabled=True)
