# ui/app.py
import json
import time
from typing import Any, Dict, List

import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="The Coding Penguins – Entity Extractor", layout="wide")

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:8000"
if "last_results" not in st.session_state:
    st.session_state.last_results = None

def post_json(path: str, payload: Dict[str, Any], timeout: int = 600) -> Dict[str, Any]:
    url = f"{st.session_state.api_url}{path}"
    r = requests.post(url, json=payload, timeout=timeout)
    try:
        return r.json()
    except Exception:
        return {"error": f"Invalid JSON response from {url} (status={r.status_code})"}

def get_json(path: str, timeout: int = 20) -> Dict[str, Any]:
    url = f"{st.session_state.api_url}{path}"
    r = requests.get(url, timeout=timeout)
    try:
        return r.json()
    except Exception:
        return {"error": f"Invalid JSON response from {url} (status={r.status_code})"}

def to_dataframe(entities: List[Dict[str, Any]]) -> pd.DataFrame:
    if not entities:
        return pd.DataFrame(columns=["name","title","org","context_url","snippet","score","sem_score"])
    df = pd.DataFrame(entities)
    for col in ["name","title","org","context_url","snippet","score","sem_score"]:
        if col not in df.columns:
            df[col] = None
    if "score" in df.columns:
        df = df.sort_values(by=["score","sem_score"], ascending=False)
    return df

def download_bytes(df: pd.DataFrame, kind: str = "json") -> bytes:
    if kind == "json":
        return df.to_json(orient="records", force_ascii=False).encode("utf-8")
    if kind == "csv":
        return df.to_csv(index=False).encode("utf-8")
    return b""

with st.sidebar:
    st.title("Settings")
    api_url_input = st.text_input("API URL", value=st.session_state.api_url, key="api_url_input")
    if api_url_input != st.session_state.api_url:
        st.session_state.api_url = api_url_input

    cA, cB = st.columns(2)
    with cA:
        if st.button("Check API Health", key="health_btn"):
            data = get_json("/health", timeout=6)
            if "error" in data: st.error(data["error"])
            else: st.success(data)
    with cB:
        if st.button("Clear Results", key="clear_btn"):
            st.session_state.last_results = None
            st.info("Cleared results.")
    st.markdown("---")
    st.caption("Run API:  set CP_IGNORE_ROBOTS=1  &&  python -m uvicorn api.main:app --reload --port 8000")

st.title("The Coding Penguins — Automated Entity Extraction")
tab1, tab2 = st.tabs(["Crawl a Domain (End-to-End)", "Single Page Extract"])

with tab1:
    st.subheader("Crawl a Domain and Extract Entities")

    col1, col2 = st.columns([3,2])
    with col1:
        domain = st.text_input("Domain (include https://)", placeholder="https://example.gov", key="crawl_domain")
        keywords_str = st.text_input("Keywords (comma-separated; optional in Auto)", value="", key="crawl_keywords")
    with col2:
        max_pages = st.number_input("Max Pages", min_value=10, max_value=2000, value=30, step=10, key="crawl_max_pages")
        max_depth = st.number_input("Max Depth", min_value=0, max_value=6, value=2, step=1, key="crawl_max_depth")

    colt1, colt2 = st.columns([2,2])
    with colt1:
        target_type_ui = st.selectbox(
            "Target Type",
            ["auto (recommended)","person","alumni","judge","minister","tech_term","org","location","generic"],
            index=0, key="target_type_select", help="Auto infers keywords + types using local models."
        )
    with colt2:
        use_semantic = st.checkbox("Use Semantic AI (local)", value=True, key="use_semantic_chk",
                                   help="Local embeddings re-rank relevant paragraphs before extraction.")

    ex1, ex2, ex3, ex4 = st.columns(4)
    with ex1:
        if st.button("Use Example: India MoHFW", key="ex1"): domain = "https://main.mohfw.gov.in"
    with ex2:
        if st.button("Use Example: US DOJ", key="ex2"): domain = "https://www.justice.gov"
    with ex3:
        if st.button("Use Example: UK Cabinet Office", key="ex3"): domain = "https://www.gov.uk/government/organisations/cabinet-office"
    with ex4:
        if st.button("Use Example: AU AGD", key="ex4"): domain = "https://www.ag.gov.au"

    run = st.button("🚀 Crawl & Extract", type="primary", key="crawl_run")

    if run:
        payload = {
            "domain": domain.strip(),
            "keywords": [k.strip() for k in keywords_str.split(",") if k.strip()],
            "max_pages": int(max_pages),
            "max_depth": int(max_depth),
            "target_type": "auto" if target_type_ui.startswith("auto") else target_type_ui,
            "semantic": bool(use_semantic),
        }
        with st.spinner("Crawling and extracting…"):
            t0 = time.time()
            data = post_json("/crawl-and-extract", payload, timeout=900)
            t1 = time.time()

        if "error" in data:
            st.error(f"Failed: {data.get('error')}")
        else:
            st.session_state.last_results = data
            pages_scanned = int(data.get("pages_scanned", 0))
            entities = data.get("entities", []) or []
            used_sem = data.get("used_semantic", False)
            auto_types = data.get("auto_types", [])
            expanded = data.get("expanded_keywords", [])
            st.success(f"✅ Done in {t1 - t0:.1f}s — Scanned {pages_scanned} pages; Found {len(entities)} entities")
            st.caption(
                f"Target type: **{data.get('target_type','auto')}** • "
                f"Semantic AI: **{used_sem}** • "
                f"Inferred types: **{', '.join(auto_types) or '—'}** • "
                f"Expanded terms: {', '.join(expanded[:8]) or '—'}"
            )

    if st.session_state.last_results:
        res = st.session_state.last_results
        st.markdown(
            f"**Domain:** [{res.get('domain','–')}]({res.get('domain','')})"
            f" • **Pages scanned:** {res.get('pages_scanned',0)}"
            f" • **Entities:** {len(res.get('entities',[]))}"
        )

        with st.expander("Filters & View", expanded=True):
            f1, f2, f3 = st.columns(3)
            with f1:
                min_score = st.slider("Min Score", min_value=0.0, max_value=0.99, value=0.60, step=0.01, key="flt_min_score")
            with f2:
                title_contains = st.text_input("Title contains", value="", key="flt_title")
            with f3:
                name_contains = st.text_input("Name contains", value="", key="flt_name")

        df = to_dataframe(res.get("entities", []))
        if "score" in df: df = df[df["score"] >= float(min_score)]
        if title_contains.strip():
            df = df[df["title"].fillna("").str.contains(title_contains.strip(), case=False, na=False)]
        if name_contains.strip():
            df = df[df["name"].fillna("").str.contains(name_contains.strip(), case=False, na=False)]

        st.dataframe(df, use_container_width=True, height=440)

        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button("⬇️ Download JSON", download_bytes(df, "json"), "entities.json",
                               "application/json", use_container_width=True, key="dl_json")
        with d2:
            st.download_button("⬇️ Download CSV", download_bytes(df, "csv"), "entities.csv",
                               "text/csv", use_container_width=True, key="dl_csv")
        with d3:
            if st.button("Show snippets & sources", key="show_snips"):
                for _, row in df.iterrows():
                    title = row.get("title") or ""
                    name = row.get("name") or "?"
                    with st.expander(f"{name} — {title}", expanded=False):
                        st.markdown(f"**Score:** {row.get('score','')}, **Semantic:** {row.get('sem_score','')}")
                        url = row.get("context_url", "")
                        if url: st.markdown(f"[Source]({url})")
                        st.write(row.get("snippet",""))

with tab2:
    st.subheader("Extract Entities from a Single Page")
    c1, c2 = st.columns([3,2])
    with c1:
        page_url = st.text_input("Page URL (include https://)", placeholder="https://example.gov/ministers", key="single_url")
        k_single = st.text_input("Keywords (comma-separated)", value="minister, judge, secretary", key="single_keywords")
    with c2:
        run_single = st.button("🔎 Extract from Page", key="single_run")

    if run_single:
        payload = {"url": page_url.strip(), "keywords": [k.strip() for k in k_single.split(",") if k.strip()]}
        with st.spinner("Fetching & extracting…"):
            data = post_json("/extract", payload, timeout=200)
        if "error" in data:
            st.error(f"Failed: {data.get('error')}")
        else:
            ents = data.get("entities", []) or []
            st.success(f"✅ Found {len(ents)} entities from: {data.get('url','')}")
            df = to_dataframe(ents)
            st.dataframe(df, use_container_width=True, height=380)
            cA, cB = st.columns(2)
            with cA:
                st.download_button("⬇️ JSON", download_bytes(df, "json"), "entities_single.json",
                                   "application/json", use_container_width=True, key="single_dl_json")
            with cB:
                st.download_button("⬇️ CSV", download_bytes(df, "csv"), "entities_single.csv",
                                   "text/csv", use_container_width=True, key="single_dl_csv")

st.markdown("---")
st.caption("© The Coding Penguins — Deviathon 2025 • FastAPI + Streamlit + spaCy + MiniLM (local). No cloud LLMs used.")
