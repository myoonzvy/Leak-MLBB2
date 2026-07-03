"""
scan.py — headless scanner for GitHub Actions.
Scans all 5RVE?? URLs and writes results.json
"""
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "https://survey.moontontech.net/t/5RVE"
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
RESULTS_FILE = "results.json"


def check_url(first, second):
    url = BASE_URL + first + second
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        return first, second, r.status_code
    except requests.RequestException:
        return first, second, 0


def run_scan():
    tasks = [(f, s) for f in ALPHABET for s in ALPHABET]
    results = {f: {} for f in ALPHABET}
    total = len(tasks)
    done = 0

    print(f"Scanning {total} URLs with 20 workers...")

    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = [ex.submit(check_url, f, s) for f, s in tasks]
        for fut in as_completed(futures):
            first, second, status = fut.result()
            results[first][second] = status
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{total} ({done/total*100:.1f}%)")

    print(f"Scan complete. {done} URLs checked.")
    return results


def build_html(results):
    """Generate index.html from scan results."""

    ALPHABET_LIST = list(ALPHABET)
    BASE = BASE_URL

    # Compute stats per prefix
    groups = []
    for f in ALPHABET_LIST:
        good = sum(1 for s in ALPHABET_LIST if results.get(f, {}).get(s) == 200)
        # all_slots: (href, label, is_working)
        all_slots = [
            (BASE + f + s, f + s, results.get(f, {}).get(s) == 200)
            for s in ALPHABET_LIST
        ]
        links = [(BASE + f + s, f + s) for s in ALPHABET_LIST if results.get(f, {}).get(s) == 200]

        if good == 62:
            badge_type = "full"
        elif good == 0:
            badge_type = "dead"
        else:
            badge_type = "partial"

        groups.append({
            "prefix": f,
            "badge_type": badge_type,
            "count": f"{good}/62",
            "good": good,
            "links": links,
            "all_slots": all_slots,
        })

    # Sort: partial first (open), then full, then dead
    partial_groups = [g for g in groups if g["badge_type"] == "partial"]
    full_groups    = [g for g in groups if g["badge_type"] == "full"]
    dead_groups    = [g for g in groups if g["badge_type"] == "dead"]

    total_good = sum(g["good"] for g in groups)
    dead_prefixes = [g["prefix"] for g in dead_groups]

    partial_callout = " &middot; ".join(
        f'<code>{g["prefix"]}</code> &mdash; {g["count"]}' for g in partial_groups
    ) or "None"
    dead_callout = ", ".join(f'<code>{p}</code>' for p in dead_prefixes) or "None"

    def render_group(g, open_attr=""):
        badge_class = "badge-partial" if g["badge_type"] == "partial" else "badge-full" if g["badge_type"] == "full" else "badge-dead"
        links_html = "".join(
            f'        <a href="{href}" target="_blank" rel="noopener">{label}</a>\n'
            if working else
            f'        <span class="dead" title="Not working">{label}</span>\n'
            for href, label, working in g["all_slots"]
        )
        return f'''    <details class="prefix-group"{open_attr} data-prefix="{g["prefix"]}">
      <summary>
        <span class="badge {badge_class}">{g["count"]}</span>
        <span class="prefix-label">Prefix <code>{g["prefix"]}</code></span>
        <span class="link-count">{g["good"]} working / {62 - g["good"]} dead</span>
      </summary>
      <div class="links-grid">
{links_html}      </div>
    </details>
'''

    sections_html = ""
    if partial_groups:
        sections_html += '  <div class="section-label"><span class="dot"></span> Partial Prefixes &mdash; Expanded</div>\n'
        for g in partial_groups:
            sections_html += render_group(g, ' open')

    if full_groups:
        sections_html += '\n  <div class="section-label full-section"><span class="dot" style="background:var(--muted)"></span> Full Prefixes &mdash; All 62/62 Active</div>\n'
        for g in full_groups:
            sections_html += render_group(g)

    if dead_groups:
        sections_html += '\n  <div class="section-label dead-section"><span class="dot" style="background:#ef4444"></span> Dead Prefixes &mdash; No Active Links</div>\n'
        for g in dead_groups:
            sections_html += render_group(g)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>5RV4 Survey &mdash; Active Links</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Sora:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0d0f14; --surface: #161b24; --surface2: #1e2635;
    --border: #2a3347; --text: #c9d1e0; --muted: #5a6a85;
    --accent: #4f9cf9; --orange: #f97316;
    --mono: 'JetBrains Mono', monospace; --sans: 'Sora', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: var(--sans); background: var(--bg); color: var(--text); min-height: 100vh; }}
  header {{ background: linear-gradient(135deg,#0d1520 0%,#111827 50%,#0d1520 100%); border-bottom: 1px solid var(--border); padding: 2.5rem 2rem 2rem; position: relative; overflow: hidden; }}
  header::before {{ content:''; position:absolute; inset:0; background: radial-gradient(ellipse at 20% 50%,rgba(79,156,249,.06) 0%,transparent 60%), radial-gradient(ellipse at 80% 50%,rgba(249,115,22,.04) 0%,transparent 60%); pointer-events:none; }}
  .header-inner {{ max-width:1200px; margin:0 auto; position:relative; }}
  .header-tag {{ font-family:var(--mono); font-size:.7rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:var(--accent); background:rgba(79,156,249,.1); border:1px solid rgba(79,156,249,.25); border-radius:4px; padding:3px 10px; display:inline-block; margin-bottom:.8rem; }}
  h1 {{ font-family:var(--mono); font-size:clamp(1.6rem,4vw,2.4rem); font-weight:700; color:#e8f0ff; letter-spacing:-.02em; margin-bottom:.5rem; }}
  h1 span {{ color:var(--accent); }}
  .header-meta {{ font-size:.875rem; color:var(--muted); display:flex; flex-wrap:wrap; gap:1.5rem; margin-top:1rem; align-items:center; }}
  .header-meta a {{ color:var(--accent); text-decoration:none; font-family:var(--mono); font-size:.8rem; }}
  .header-meta a:hover {{ text-decoration:underline; }}
  .stat-pill {{ display:inline-flex; align-items:center; gap:6px; background:var(--surface); border:1px solid var(--border); border-radius:20px; padding:4px 12px; font-size:.8rem; }}
  .stat-pill .num {{ color:#22c55e; font-family:var(--mono); font-weight:700; }}
  .updated-pill {{ display:inline-flex; align-items:center; gap:6px; background:rgba(79,156,249,.07); border:1px solid rgba(79,156,249,.2); border-radius:20px; padding:4px 12px; font-size:.75rem; font-family:var(--mono); color:var(--muted); }}
  .callouts {{ max-width:1200px; margin:1.5rem auto 0; padding:0 2rem; display:flex; flex-wrap:wrap; gap:.75rem; }}
  .callout {{ flex:1; min-width:260px; padding:12px 16px; border-radius:8px; font-size:.85rem; display:flex; align-items:flex-start; gap:10px; }}
  .callout-icon {{ font-size:1rem; flex-shrink:0; margin-top:1px; }}
  .callout.interesting {{ background:rgba(249,115,22,.08); border:1px solid rgba(249,115,22,.25); }}
  .callout.interesting .callout-title {{ color:var(--orange); }}
  .callout.dead {{ background:rgba(255,255,255,.03); border:1px solid var(--border); }}
  .callout.dead .callout-title {{ color:var(--muted); }}
  .callout-title {{ font-weight:700; margin-bottom:4px; font-size:.78rem; text-transform:uppercase; letter-spacing:.05em; }}
  .callout code {{ font-family:var(--mono); font-size:.8rem; background:rgba(255,255,255,.07); padding:1px 6px; border-radius:3px; color:var(--text); }}
  main {{ max-width:1200px; margin:0 auto; padding:2rem; }}
  .search-bar {{ position:relative; margin-bottom:1rem; }}
  .search-bar input {{ width:100%; padding:11px 16px 11px 44px; font-size:.95rem; font-family:var(--mono); background:var(--surface); border:1px solid var(--border); border-radius:8px; color:var(--text); outline:none; transition:border-color .2s,box-shadow .2s; }}
  .search-bar input:focus {{ border-color:var(--accent); box-shadow:0 0 0 3px rgba(79,156,249,.15); }}
  .search-bar input::placeholder {{ color:var(--muted); }}
  .search-icon {{ position:absolute; left:14px; top:50%; transform:translateY(-50%); color:var(--muted); font-size:1.1rem; pointer-events:none; }}
  .search-hint {{ font-size:.75rem; color:var(--muted); margin-bottom:1.5rem; min-height:1rem; }}
  .section-label {{ font-family:var(--mono); font-size:.7rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); border-bottom:1px solid var(--border); padding-bottom:8px; margin:1.5rem 0 1rem; display:flex; align-items:center; gap:8px; }}
  .dot {{ display:inline-block; width:3px; height:14px; border-radius:2px; background:var(--orange); }}
  .prefix-group {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; margin-bottom:8px; overflow:hidden; transition:border-color .15s; }}
  .prefix-group:hover {{ border-color:#3a4a66; }}
  .prefix-group summary {{ cursor:pointer; list-style:none; padding:12px 16px; display:flex; align-items:center; gap:10px; user-select:none; font-size:.9rem; }}
  .prefix-group summary::-webkit-details-marker {{ display:none; }}
  .prefix-group summary::after {{ content:'\\25B8'; margin-left:auto; color:var(--muted); font-size:.75rem; transition:transform .2s; }}
  .prefix-group[open] summary::after {{ transform:rotate(90deg); }}
  .prefix-group summary:hover .prefix-label {{ color:var(--accent); }}
  .badge {{ font-family:var(--mono); font-size:.72rem; font-weight:700; padding:3px 10px; border-radius:20px; min-width:52px; text-align:center; flex-shrink:0; }}
  .badge-partial {{ background:rgba(249,115,22,.15); color:var(--orange); border:1px solid rgba(249,115,22,.3); }}
  .badge-full {{ background:rgba(255,255,255,.05); color:var(--muted); border:1px solid var(--border); }}
  .badge-dead {{ background:rgba(239,68,68,.1); color:#ef4444; border:1px solid rgba(239,68,68,.3); }}
  .prefix-label {{ font-size:.9rem; color:var(--text); transition:color .15s; }}
  .prefix-label code {{ font-family:var(--mono); font-weight:700; color:#e8f0ff; font-size:.95rem; }}
  .link-count {{ font-family:var(--mono); font-size:.72rem; color:var(--muted); }}
  .links-grid {{ padding:4px 16px 14px; display:grid; grid-template-columns:repeat(auto-fill,minmax(72px,1fr)); gap:5px; }}
  .links-grid a {{ padding:6px 8px; background:rgba(34,197,94,.12); border:1px solid rgba(34,197,94,.35); border-radius:6px; text-decoration:none; color:#4ade80; font-family:var(--mono); font-size:.78rem; text-align:center; transition:background .12s,border-color .12s,color .12s,transform .1s; display:block; }}
  .links-grid a:hover {{ background:rgba(34,197,94,.25); border-color:rgba(34,197,94,.6); color:#86efac; transform:translateY(-1px); }}
  .links-grid span.dead {{ padding:6px 8px; background:rgba(239,68,68,.08); border:1px solid rgba(239,68,68,.25); border-radius:6px; color:#f87171; font-family:var(--mono); font-size:.78rem; text-align:center; display:block; opacity:.7; cursor:not-allowed; }}
  footer {{ border-top:1px solid var(--border); padding:1.5rem 2rem; text-align:center; font-size:.75rem; color:var(--muted); max-width:1200px; margin:2rem auto 0; }}
  #no-results {{ display:none; text-align:center; padding:3rem; color:var(--muted); font-size:.9rem; }}
  @media(max-width:640px) {{ header{{padding:1.5rem 1rem;}} main{{padding:1.5rem 1rem;}} .callouts{{padding:0 1rem;}} .links-grid{{grid-template-columns:repeat(auto-fill,minmax(60px,1fr));}} }}
</style>
</head>
<body>
<header>
  <div class="header-inner">
    <div class="header-tag">Survey Link Scanner</div>
    <h1>Active Links &mdash; <span>5RV4??</span></h1>
    <div class="header-meta">
      <span>Base URL: <a href="https://survey.moontontech.net/t/5RV4" target="_blank" rel="noopener">survey.moontontech.net/t/5RV4</a></span>
      <span class="stat-pill">&#10004; <span class="num">{total_good:,}</span>&nbsp;working out of 3,844 scanned</span>
      <span class="updated-pill">&#128336; Last scan: {now}</span>
    </div>
  </div>
</header>

<div class="callouts">
  <div class="callout interesting">
    <span class="callout-icon">&#9889;</span>
    <div>
      <div class="callout-title">Partial Prefixes (some broken)</div>
      {partial_callout}
    </div>
  </div>
  <div class="callout dead">
    <span class="callout-icon">&#10007;</span>
    <div>
      <div class="callout-title">Dead Prefixes (HTTP 500 / no response)</div>
      {dead_callout}
    </div>
  </div>
</div>

<main>
  <div class="search-bar">
    <span class="search-icon">&#128269;</span>
    <input type="text" id="filter" placeholder="Filter by code (e.g. Ba, n7, 5Q)..." autocomplete="off" spellcheck="false">
  </div>
  <p class="search-hint" id="result-count"></p>

{sections_html}
  <div id="no-results">No links match your filter.</div>
</main>

<footer>
  Auto-updated by GitHub Actions &nbsp;&middot;&nbsp; <strong>5RV4</strong> survey link space &nbsp;&middot;&nbsp; Last scan: {now}
</footer>

<script>
const filterInput = document.getElementById('filter');
const noResults = document.getElementById('no-results');
const resultCount = document.getElementById('result-count');
const sectionLabels = document.querySelectorAll('.section-label');

filterInput.addEventListener('input', () => {{
  const q = filterInput.value.trim().toLowerCase();
  const groups = document.querySelectorAll('.prefix-group');
  let totalLinks = 0;
  groups.forEach(group => {{
    const links = group.querySelectorAll('.links-grid a');
    if (!q) {{ links.forEach(a => a.style.display = ''); group.style.display = ''; return; }}
    let anyMatch = false;
    links.forEach(a => {{
      const match = a.textContent.toLowerCase().includes(q);
      a.style.display = match ? '' : 'none';
      if (match) {{ anyMatch = true; totalLinks++; }}
    }});
    group.style.display = anyMatch ? '' : 'none';
    if (anyMatch) group.open = true;
  }});
  if (q) {{
    resultCount.textContent = totalLinks + ' link(s) matched';
    noResults.style.display = totalLinks === 0 ? 'block' : 'none';
    sectionLabels.forEach(l => l.style.display = 'none');
  }} else {{
    resultCount.textContent = '';
    noResults.style.display = 'none';
    sectionLabels.forEach(l => l.style.display = '');
  }}
}});
</script>
</body>
</html>'''

    return html


if __name__ == "__main__":
    results = run_scan()

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f)
    print(f"Saved {RESULTS_FILE}")

    html = build_html(results)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved index.html")
