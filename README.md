# Yixing Dashboards — Public App Shell

Public Streamlit app that serves the Yixing dashboards. **This repo contains no
business data.** The dashboard HTML files live in the private repo
[`yanruong/yixing-dashboard-live`](https://github.com/yanruong/yixing-dashboard-live)
and are fetched at runtime with a read-only GitHub token, only after the viewer
passes a server-side password check.

Two dashboards are served behind one login, selected with a toggle at the top:

| Toggle       | Private file          | Built by                  |
|--------------|-----------------------|---------------------------|
| Goldsmith    | `dashboard.html`      | `fetch_and_build.py`      |
| Bulk Chain   | `dashboard_bulk.html` | `fetch_and_build_bulk.py` |

Only the dashboard currently selected is fetched (each cached independently for
5 minutes), so the toggle never loads both at once — switching is a quick reload
the first time, then instant from cache.

Why this shape: Streamlit Community Cloud allows only one *private* app per
workspace. A public app whose data is fetched from a private repo behind
Streamlit secrets sidesteps the limit without exposing anything.

## Required Streamlit secrets

```toml
GITHUB_TOKEN = "github_pat_..."   # fine-grained PAT, contents:read on yixing-dashboard-live only
DASHBOARD_PASSWORD = "..."        # viewer password (server-side gate for the whole app)
```

Each dashboard also has its own built-in JS gate (a different password baked
into each HTML). The shell reads that value back from the file and pre-authorises
it, so viewers only ever type the one `DASHBOARD_PASSWORD` above.

## Update flow

Nothing in this repo changes week to week. The refresh workflow lives in
`~/Downloads/yixing-dashboard/`:

1. `fetch_and_build.py` (VPN + SSH tunnel) regenerates `dashboard.html`
2. `fetch_and_build_bulk.py` (VPN + SSH tunnel) regenerates `dashboard_bulk.html`
3. `publish.sh` pushes both to the private data repo

The app caches the HTML for 5 minutes, so the live site shows a new push within
~5 minutes without any redeploy. Adding a third dashboard is just another row in
`DASHBOARDS` in `streamlit_app.py` plus another file in `publish.sh`.
