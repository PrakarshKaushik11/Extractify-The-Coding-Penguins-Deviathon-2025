# ui/app.py
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import streamlit as st

REQUEST_TIMEOUT = 600

st.set_page_config(page_title="The Coding Penguins — Automated Entity Extraction", layout="wide")

# --- session state defaults
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:8000"

# --- sidebar
st.sidebar.title("Deploy")
st.sidebar.markdown("Run API:")
st.sidebar.code("uvicorn api.main:app --reload --port 8000", language="bash")

# --- Header
st.title("The Coding Penguins — Automated Entity Extraction")

# Tabs
tab1, tab2 = st.tabs(["Crawl a Domain (End-to-End)", "Single Page Extract"])


def _post(api: str, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    url = f"{api.rstrip('/')}{path}"
    try:
        r = requests.post(url, json=payload, timeout=60)
        if r.status_code == 404 and path == "/crawl-and-extract":
            return None  # allow fallback
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


def _get(api: str, path: str) -> Optional[Any]:
    url = f"{api.rstrip('/')}{path}"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


with tab1:
    # --- Controls
    colA, colB = st.columns([4, 1.2])
    with colA:
        api_url = st.text_input("API URL", value=st.session_state.api_url, key="api_url")
    with colB:
        pass

    domain = st.text_input("Domain (include https://)", "https://www.justice.gov")
    keywords = st.text_input(
        "Keywords (comma-separated; optional in Auto)",
        "minister, judge, secretary",
    )
    cols = st.columns(2)
    with cols[0]:
        max_pages = st.number_input("Max Pages", 1, 200, 30, step=1)
    with cols[1]:
        max_depth = st.number_input("Max Depth", 1, 6, 2, step=1)

    st.markdown("**Target Type**")
    target = st.selectbox(" ", options=["auto (recommended)", "alumni", "leadership", "legal"], index=0, label_visibility="collapsed")
    use_sem = st.checkbox("Use Semantic AI (local)", value=True)

    c1, c2, c3 = st.columns([1.2, 1.2, 6])
    with c1:
        if st.button("Use Example: India MoHFW"):
            domain = "https://mohfw.gov.in"
            st.experimental_rerun()
    with c2:
        if st.button("Use Example: US DOJ"):
            domain = "https://www.justice.gov"
            st.experimental_rerun()

    run = st.button("🧭 Crawl & Extract", type="primary")

    if run:
        payload = {
            "domain": domain.strip(),
            "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
            "max_pages": int(max_pages),
            "max_depth": int(max_depth),
        }

        with st.spinner("Crawling + extracting..."):
            # try combined endpoint first
            combo = _post(api_url, "/crawl-and-extract", payload)
            if combo is None:
                # fallback to two-step if /crawl-and-extract not available
                crawl_res = _post(api_url, "/crawl", payload)
                if crawl_res:
                    _ = _post(api_url, "/extract", {"keywords": payload["keywords"], "target": "auto"})
                res = _get(api_url, "/results")
            else:
                res = combo.get("extract", {}).get("entities") or _get(api_url, "/results")

        if not res:
            st.success("Done in 0.0s — Scanned 0 pages; Found 0 entities")
        else:
            st.success("Done — results loaded.")

    # --- results area
    data = _get(st.session_state.api_url, "/results") or []
    st.markdown(f"**Domain:** _—_ • **Pages scanned:** _?_ • **Entities:** {len(data)}")

    with st.expander("Filters & View", expanded=True):
        min_score = st.slider("Min Score", 0.0, 0.99, 0.60, 0.01)
        colf1, colf2 = st.columns(2)
        with colf1:
            title_contains = st.text_input("Title contains", "")
        with colf2:
            name_contains = st.text_input("Name contains", "")

    # Filter in-memory
    rows = []
    for e in data:
        if e.get("score") is not None and float(e.get("score")) < min_score:
            continue
        if title_contains and (not (e.get("title") or "") or title_contains.lower() not in (e.get("title") or "").lower()):
            continue
        if name_contains and (not (e.get("name") or "") or name_contains.lower() not in (e.get("name") or "").lower()):
            continue
        rows.append(e)

    df = pd.DataFrame(rows or [], columns=["name", "title", "org", "context_url", "snippet", "score"])
    st.dataframe(df, use_container_width=True)

    colD, colE, colF = st.columns([1, 1, 2])
    with colD:
        if st.button("💾 Download JSON"):
            st.download_button("Save entities.json", data=json.dumps(rows, indent=2), file_name="entities.json", mime="application/json")
    with colE:
        if st.button("⬇️ Download CSV"):
            st.download_button("Save entities.csv", data=df.to_csv(index=False), file_name="entities.csv", mime="text/csv")
    with colF:
        st.button("Show snippets & sources")  # placeholder (UI only)

with tab2:
    st.info("Single Page Extract coming soon (demo focuses on full-domain flow).")
