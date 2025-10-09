import json
import time
import requests
import streamlit as st

st.set_page_config(page_title="The Coding Penguins – Entity Extractor", layout="wide")

# ---- Sidebar: API config ----
st.sidebar.title("Settings")
api_url = st.sidebar.text_input("API URL", value="http://127.0.0.1:8000")
if st.sidebar.button("Check API Health"):
    try:
        r = requests.get(f"{api_url}/health", timeout=5)
        st.sidebar.success(f"API OK: {r.json()}")
    except Exception as e:
        st.sidebar.error(f"API error: {e}")

st.title("🧊 The Coding Penguins – Automated Entity Extraction")

# ---- Inputs ----
domain = st.text_input("Domain URL (optional for now)", "https://example.com")
keywords = st.text_input("Keywords (comma-separated)", "minister, judge")
max_depth = st.number_input("Max Depth", min_value=0, max_value=3, value=1)

col1, col2, col3 = st.columns(3)

def post_json(path, payload):
    try:
        resp = requests.post(f"{api_url}{path}", json=payload, timeout=120)
        return True, resp.json()
    except Exception as e:
        return False, {"error": str(e)}

def get_json(path):
    try:
        resp = requests.get(f"{api_url}{path}", timeout=30)
        return True, resp.json()
    except Exception as e:
        return False, {"error": str(e)}

with col1:
    if st.button("Start Crawl"):
        with st.spinner("Crawling..."):
            ok, res = post_json("/crawl", {
                "domain": domain,
                "max_depth": int(max_depth),
                "keywords": keywords
            })
            if ok and res.get("ok", False):
                st.success("Crawl completed.")
            else:
                st.error(f"Crawl failed: {json.dumps(res, indent=2)}")

with col2:
    if st.button("Run Extraction"):
        with st.spinner("Extracting entities..."):
            ok, res = post_json("/extract", {
                "input_path": "data/pages.jsonl",
                "out_path": "data/entities.json",
                "keywords": keywords
            })
            if ok and res.get("ok", False):
                st.success("Extraction completed.")
            else:
                st.error(f"Extraction failed: {json.dumps(res, indent=2)}")

with col3:
    if st.button("Refresh Results"):
        st.experimental_rerun()

# ---- Results ----
st.subheader("Results")
ok, res = get_json("/results")
if ok:
    entities = res.get("entities", [])
    st.caption(f"{len(entities)} entities")
    if entities:
        # Show as table
        st.dataframe(entities, use_container_width=True)
        # Download buttons
        st.download_button("Download JSON", data=json.dumps(res, ensure_ascii=False, indent=2),
                           file_name="entities.json", mime="application/json")
    else:
        st.info("No entities yet. Try Run Extraction.")
else:
    st.error(f"Could not fetch results: {res.get('error')}")
