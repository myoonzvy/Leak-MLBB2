# msurvey — 5RV4 Survey Link Scanner

Auto-scans all `5RV4??` URLs and publishes a live viewer to GitHub Pages.

## Setup (one-time)

### 1. Create the repo & upload files

Upload these files to a new GitHub repo:
```
index.html          ← the viewer (auto-updated by Actions)
scan.py             ← the scanner script
results.json        ← last scan results (auto-updated)
.github/
  workflows/
    scan.yml        ← the automation
```

### 2. Enable GitHub Pages

- Go to **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: `main`, folder: `/ (root)`
- Click Save

Your site will be live at `https://<your-username>.github.io/<repo-name>/`

### 3. Done!

- The scanner runs **automatically every day at 06:00 UTC**
- To trigger a manual scan: go to **Actions → Scan & Deploy → Run workflow**
- Each run updates `index.html` and `results.json` and commits them back

## Files

| File | Description |
|------|-------------|
| `scan.py` | Scans all 3,844 URLs and builds `index.html` |
| `index.html` | The viewer website (static, no server needed) |
| `results.json` | Raw scan results (status codes per URL) |
| `.github/workflows/scan.yml` | Daily automation |
