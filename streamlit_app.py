"""Public Streamlit app that serves the Yixing Goldsmith dashboard.

Contains NO data. On correct password entry it fetches dashboard.html from the
private repo yanruong/yixing-dashboard-live using a read-only GitHub token kept
in Streamlit secrets, then embeds it full-screen. Nothing is sent to the
browser until the password check passes server-side.

Required secrets (Streamlit Cloud -> app settings -> Secrets):
  GITHUB_TOKEN       = fine-grained PAT, contents:read on yixing-dashboard-live
  DASHBOARD_PASSWORD = viewer password
"""
import hmac
import re
import time

import requests
import streamlit as st
import streamlit.components.v1 as components

DATA_REPO = "yanruong/yixing-dashboard-live"
DATA_FILE = "dashboard.html"

st.set_page_config(
    page_title="Yixing Goldsmith Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def password_ok() -> bool:
    if st.session_state.get("auth_ok"):
        return True

    def check():
        entered = st.session_state.get("pw", "")
        if hmac.compare_digest(entered, st.secrets["DASHBOARD_PASSWORD"]):
            st.session_state["auth_ok"] = True
            st.session_state["pw"] = ""  # don't keep the password around
        else:
            fails = st.session_state.get("fails", 0) + 1
            st.session_state["fails"] = fails
            # Escalating delay makes brute-forcing impractical
            time.sleep(min(2 ** fails, 30))
            st.session_state["auth_error"] = True

    locked = st.session_state.get("fails", 0) >= 8
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.markdown("### Yixing Goldsmith")
        if locked:
            st.error("Too many failed attempts — reload the page to try again.")
        else:
            st.text_input("Password", type="password", key="pw", on_change=check)
            if st.session_state.get("auth_error"):
                st.error("Incorrect password")
    return False


@st.cache_data(ttl=300, show_spinner="Loading latest dashboard…")
def fetch_dashboard() -> str:
    resp = requests.get(
        f"https://api.github.com/repos/{DATA_REPO}/contents/{DATA_FILE}",
        params={"ref": "main"},
        headers={
            "Authorization": f"Bearer {st.secrets['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github.raw",
        },
        timeout=60,
    )
    resp.raise_for_status()
    html = resp.content.decode("utf-8")
    # Pre-authorise the dashboard's built-in JS gate so viewers aren't asked
    # twice — Streamlit already gated server-side. Setting sessionStorage makes
    # the gate script hide itself, but the .app container starts display:none
    # inline and only checkPw() reveals it, so show it explicitly at end of body.
    m = re.search(r"PW\s*=\s*'([^']+)'", html)
    if m:
        set_auth = f"<script>sessionStorage.setItem('yx_auth','{m.group(1)}');</script>"
        html = re.sub(r"(<body[^>]*>)", r"\1" + set_auth, html, count=1)
        reveal = (
            "<script>"
            "var g=document.getElementById('pw-gate');if(g)g.style.display='none';"
            "var a=document.querySelector('.app');if(a)a.style.display='';"
            "</script>"
        )
        html = html.replace("</body>", reveal + "</body>", 1)
    return html


if password_ok():
    st.markdown(
        """
        <style>
          header[data-testid="stHeader"] {display: none;}
          div[data-testid="stToolbar"] {display: none;}
          .block-container {padding: 0 !important; max-width: 100% !important;}
          div[data-testid="stAppViewContainer"] {overflow: hidden;}
          iframe {height: 100vh !important; width: 100% !important; border: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(fetch_dashboard(), height=900, scrolling=True)
