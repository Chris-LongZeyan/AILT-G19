from html import escape
from pathlib import Path
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from lostfound.config import load_settings, ROOT
from lostfound.database import connect_database, initialize, list_items
from lostfound.matching import search, PROMPT_VERSION

st.set_page_config(page_title="Campus Find | Lost & Found", page_icon="🌿", layout="wide")
st.html("<style>" + (ROOT / "assets/style.css").read_text(encoding="utf-8") + "</style>")

@st.cache_resource(show_spinner=False)
def get_database(url):
    engine = connect_database(url)
    initialize(engine)
    return engine

def card(item, rank=None, evidence=None):
    title = escape(item.colour.title() + " " + item.type.lower())
    badge = f"Possible match {rank}" if rank else "Fictional record"
    quotes = ""
    if evidence:
        quotes = '<div class="evidence"><b>Source evidence</b><br>' + "<br>".join(
            "&ldquo;" + escape(q) + "&rdquo;" for q in evidence) + "</div>"
    st.html(f'<article class="item-card"><div class="item-top"><span class="item-id">{escape(item.id)}</span>'
            f'<span class="result-badge">{badge}</span></div><div class="item-title">{title}</div>'
            f'<div class="item-description">{escape(item.description)}</div>{quotes}</article>')

st.html('<div class="brand"><div class="brand-mark">cf.</div><div><div class="brand-name">Campus Find</div>'
        '<div class="brand-caption">Lost &amp; found matcher</div></div><div class="course-tag">AILT9019 · Group 19</div></div>')
try:
    settings = load_settings()
    engine = get_database(settings.database_url)
    catalogue = list_items(engine)
except (SQLAlchemyError, ValueError, OSError):
    st.error("The item catalogue is unavailable. Check the database configuration and restart the app.")
    st.stop()

left, right = st.columns([1.8, 1], gap="large")
with left:
    st.html('<div class="eyebrow">A little detail goes a long way</div>')
    st.html('<h1>Less searching.<br>More finding.</h1>')
    st.html('<p class="intro">A colour, a pattern, a familiar detail. Describe a fictional lost item and explore what might match.</p>')
with right:
    st.html('<aside class="hero-note"><b>Small clues. Possible matches.</b><p>Start with the item type, then add its colour or a distinctive feature. Every suggestion links back to its original record.</p></aside>')
st.html(f'<div class="meta-row"><span class="pill">{len(catalogue)} fictional items</span>'
        '<span class="pill">Up to 3 possible matches</span><span class="pill">No account needed</span></div>')

search_tab, browse_tab, about_tab = st.tabs(["Find an item", "Browse catalogue", "About this demo"])
with search_tab:
    st.subheader("What are you looking for?")
    st.caption("Course demonstration only. Enter fictional descriptions in English, without names, contacts or serial numbers.")
    mode_label = st.radio("Search method", ["Keyword search", "AI matching"], horizontal=True)
    mode = "ai" if mode_label == "AI matching" else "keyword"
    if mode == "ai":
        if settings.ai_ready:
            st.caption(f"AI provider: {settings.provider} · Model: {settings.model}. Your fictional query and the selected catalogue records are sent to this provider.")
        else:
            st.info("AI matching is waiting for the team's API configuration. Keyword search is available now.")
    else:
        st.caption("Keyword search is a word-overlap baseline. It does not understand synonyms or resolve conflicting details.")
    with st.form("search_form"):
        query = st.text_area("Describe the item", max_chars=300, height=110,
                             placeholder="For example: black insulated bottle with a silver lid")
        category = st.selectbox("Category (optional)", ["All items"] + sorted({r.type for r in catalogue}))
        submitted = st.form_submit_button("Search items", type="primary", width="stretch")
    if submitted:
        selected = [r for r in catalogue if category == "All items" or r.type == category]
        with st.spinner("Checking the catalogue…"):
            result = search(query, selected, mode, settings)
        st.session_state["result"] = result
        st.session_state["result_mode"] = mode
    result = st.session_state.get("result")
    if result and st.session_state.get("result_mode") == mode:
        st.divider()
        st.subheader("Search results")
        st.caption("AI matching" if result.mode == "ai" else "Keyword search · not AI")
        if result.status == "matches":
            st.write(result.message)
            by_id = {r.id: r for r in catalogue}
            for index, match in enumerate(result.matches, 1):
                if match.id in by_id:
                    card(by_id[match.id], index, match.evidence)
            st.caption("Suggestions do not prove ownership or authorise collection.")
        elif result.status in {"error", "invalid"}:
            st.error(result.message)
        elif result.status == "refused":
            st.warning(result.message)
        else:
            st.info(result.message)
    elif not result:
        st.caption("Try the example above. In keyword mode, LF-001 should appear first.")

with browse_tab:
    st.subheader("The fictional found-item catalogue")
    st.write("Explore the original records used by both search methods.")
    browse_category = st.selectbox("Browse by category", ["All items"] + sorted({r.type for r in catalogue}))
    visible = [r for r in catalogue if browse_category == "All items" or r.type == browse_category]
    st.caption(f"{len(visible)} records")
    columns = st.columns(2)
    for i, item in enumerate(visible):
        with columns[i % 2]:
            card(item)
with about_tab:
    st.subheader("A course project, built around careful matching")
    st.write("Campus Find explores how an AI model compares everyday descriptions with a fixed catalogue. It is an independent student demonstration, not an official HKU service.")
    st.markdown("""**How matching works**
1. Check the description and reject unsupported requests.
2. Compare it with the selected fictional records.
3. Validate every returned ID and verbatim evidence phrase.
4. Show at most three possible matches with the original descriptions.

**What this demo does not do**
It cannot verify ownership, identify owners, disclose contacts or arrange collection.
It does not access real campus posts or university systems.

**Data and privacy**
The database contains only 30 fictional records. The app does not persist queries,
search history or personal profiles. Search text remains in browser-session memory
while the page is open. AI mode sends the query and selected records to the configured
provider; that provider's retention policy applies. Keyword mode makes no model request.

**Evaluation**
The project includes a 20-query evaluation set and a separate keyword baseline.
Live AI accuracy and human usability checks remain pending. Verbatim evidence checks
do not establish semantic correctness: team members must review explanations.
The initial catalogue and implementation were AI-assisted and need team review.
""")
    st.caption(f"Prompt version: {PROMPT_VERSION} · Database: {engine.dialect.name} · Dataset: fictional-v1")
st.html('<footer class="footnote">Campus Find · AILT9019 Group 19<br>Fictional data. Possible matches. Independent verification would be required for any real-world collection.</footer>')
