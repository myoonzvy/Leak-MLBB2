import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import streamlit as st

BASE_URL = "https://survey.moontontech.net/t/5RVc"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RESULTS_FILE = Path("results.json")
WORKERS = 16

st.set_page_config(
    page_title="5RVc Survey Link Scanner",
    page_icon="🔎",
    layout="wide",
)

st.title("5RVc Survey Link Scanner")
st.caption("Green = HTTP 200 / working. Red = not working, error, timeout, or unknown.")


def empty_results():
    return {first: {} for first in ALPHABET}


def load_results():
    if not RESULTS_FILE.exists():
        return empty_results()

    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def check_code(first, second):
    code = first + second
    url = BASE_URL + code

    try:
        response = requests.get(url, timeout=12, allow_redirects=True)
        status = response.status_code

        preview = response.text[:700].lower()
        if "internal server error" in preview:
            status = 500

        return first, second, status

    except requests.RequestException:
        return first, second, 0


def live_check(prefix=None):
    if prefix:
        tasks = [(prefix, second) for second in ALPHABET]
    else:
        tasks = [(first, second) for first in ALPHABET for second in ALPHABET]

    results = empty_results()

    progress = st.progress(0)
    status_text = st.empty()

    total = len(tasks)
    done = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(check_code, first, second) for first, second in tasks]

        for future in as_completed(futures):
            first, second, status = future.result()
            results[first][second] = status
            done += 1

            if done % 10 == 0 or done == total:
                progress.progress(done / total)
                status_text.caption(f"Latest checked: {first}{second} → {status}")

    progress.empty()
    status_text.empty()

    return results


def count_working(results):
    total = len(ALPHABET) * len(ALPHABET)
    working = 0

    for first in ALPHABET:
        for second in ALPHABET:
            if results.get(first, {}).get(second) == 200:
                working += 1

    return total, working, total - working


if "results" not in st.session_state:
    st.session_state.results = load_results()
    st.session_state.source = "Saved results.json"

st.subheader("Live check")

scan_mode = st.selectbox(
    "Mode",
    ["Selected prefix only", "All prefixes"],
)

selected_prefix = st.selectbox(
    "Prefix",
    list(ALPHABET),
    index=list(ALPHABET).index("K"),
)

col_a, col_b = st.columns(2)

with col_a:
    if st.button("Run live check", use_container_width=True):
        if scan_mode == "Selected prefix only":
            new_data = live_check(selected_prefix)
            st.session_state.results[selected_prefix] = new_data[selected_prefix]
            st.session_state.source = f"Live check: prefix {selected_prefix}"
        else:
            st.session_state.results = live_check()
            st.session_state.source = "Live check: all prefixes"

        st.success("Live check finished.")

with col_b:
    if st.button("Reload saved results.json", use_container_width=True):
        st.session_state.results = load_results()
        st.session_state.source = "Saved results.json"
        st.success("Reloaded saved results.")

results = st.session_state.results
total, working, dead = count_working(results)

st.caption(f"Current data source: {st.session_state.source}")

col1, col2, col3 = st.columns(3)
col1.metric("Total Checked", total)
col2.metric("Working", working)
col3.metric("Dead / Unknown", dead)

st.divider()

search = st.text_input("Search code", placeholder="Example: Ka, dn, O9")
show_mode = st.radio("Show", ["Working only", "All links"], horizontal=True)

for first in ALPHABET:
    row = results.get(first, {})
    working_seconds = [second for second in ALPHABET if row.get(second) == 200]

    if show_mode == "Working only" and not working_seconds:
        continue

    with st.expander(f"Prefix {first} — {len(working_seconds)}/62 working"):
        cols = st.columns(5)

        index = 0

        for second in ALPHABET:
            code = first + second
            status = row.get(second)
            is_working = status == 200

            if show_mode == "Working only" and not is_working:
                continue

            if search and search.lower() not in code.lower():
                continue

            url = BASE_URL + code

            with cols[index % 5]:
                if is_working:
                    st.link_button(f"🟢 {code}", url)
                else:
                    st.button(f"🔴 {code}", disabled=True)

            index += 1

        if index == 0:
            st.caption("No matching links.")
