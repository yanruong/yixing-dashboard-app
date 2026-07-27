# Yixing Goldsmith Dashboard — Public App Shell

Public Streamlit app that serves the Yixing Goldsmith dashboard. **This repo
contains no business data.** The dashboard HTML lives in the private repo
[`yanruong/yixing-dashboard-live`](https://github.com/yanruong/yixing-dashboard-live)
and is fetched at runtime with a read-only GitHub token, only after the viewer
passes a server-side password check.

Why this shape: Streamlit Community Cloud allows only one private app per
workspace. A public app whose data is fetched from a private repo behind
Streamlit secrets sidesteps the limit without exposing anything.

## Required Streamlit secrets

```toml
GITHUB_TOKEN = "github_pat_..."   # fine-grained PAT, contents:read on yixing-dashboard-live only
DASHBOARD_PASSWORD = "..."        # viewer password (same as the dashboard's built-in gate)
```

## Update flow

Nothing in this repo changes week to week. Refresh workflow lives in
`~/Downloads/yixing-dashboard/`:

1. `fetch_and_build.py` (VPN + SSH tunnel) regenerates `dashboard.html`
2. `publish.sh` pushes it to the private data repo

The app caches the HTML for 5 minutes, so the live site shows a new push within
~5 minutes without any redeploy.
