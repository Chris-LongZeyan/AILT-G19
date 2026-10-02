"""Streamlit presentation layer for the Campus Find course demonstration."""
from html import escape

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from lostfound.config import ROOT, load_settings
from lostfound.database import connect_database, initialize, list_items
from lostfound.matching import PROMPT_VERSION, search

st.set_page_config(page_title="Campus Find", page_icon="🌿", layout="centered")
st.html("<style>" + (ROOT / "assets/style.css").read_text(encoding="utf-8") + "</style>")


@st.cache_resource(show_spinner=False)
def get_database(url):
    engine = connect_database(url)
    initialize(engine)
    return engine


def item_card(item, rank=None, evidence=None):
    """Render escaped catalogue content; arbitrary model prose is never displayed."""
    label = f"Possible match {rank}" if rank else item.type
    quotes = ""
    if evidence:
        quotes = '<div class="evidence"><span>Evidence from this record</span>' + "".join(
            "<blockquote>" + escape(quote) + "</blockquote>" for quote in evidence
        ) + "</div>"
    st.html(
        f'<article class="item-card"><div class="item-meta"><span>{escape(label)}</span>'
        f'<span class="item-id">{escape(item.id)}</span></div>'
        f'<h3>{escape(item.colour.title() + " " + item.type.lower())}</h3>'
        f'<p>{escape(item.description)}</p>{quotes}</article>'
    )


st.html(
    '<header class="app-header"><span class="wordmark">Campus Find<span class="brand-dot">.</span></span>'
    '<span class="project-label">AILT9019 · Group 19</span></header>'
)
try:
    settings = load_settings()
    engine = get_database(settings.database_url)
    catalogue = list_items(engine)
except (SQLAlchemyError, ValueError, OSError):
    st.error("The catalogue is unavailable. Check the database configuration and restart the app.")
    st.stop()

st.html('<h1>Find a lost item</h1><p class="intro">Describe its type, colour or a distinctive feature.</p>')
search_tab, browse_tab, about_tab = st.tabs(["Search", "Catalogue", "About"])

with search_tab:
    st.caption("Course demo · Fictional descriptions only. Do not enter personal details.")
    mode_label = st.radio("Search method", ["Keyword search", "AI matching"], horizontal=True)
    mode = "ai" if mode_label == "AI matching" else "keyword"
    if mode == "ai":
        if settings.ai_ready:
            st.caption(f"{settings.provider} · {settings.model}. The query and selected records are sent to this provider.")
        else:
            st.info("AI matching is not configured. Use Keyword search until the team's API key is added.")
    else:
        st.caption("Matches shared words. Synonyms and conflicting details may be missed.")

    with st.form("search_form", border=False):
        query = st.text_area(
            "Describe the item", max_chars=300, height=96,
            placeholder="e.g. black insulated bottle with a silver lid",
        )
        category = st.selectbox("Category (optional)", ["All items"] + sorted({r.type for r in catalogue}))
        submitted = st.form_submit_button("Search items", type="primary", width="stretch")

    if submitted:
        selected = [r for r in catalogue if category == "All items" or r.type == category]
        with st.spinner("Searching…"):
            result = search(query, selected, mode, settings)
        st.session_state["result"] = result
        st.session_state["result_mode"] = mode
        st.session_state["result_query"] = query

    result = st.session_state.get("result")
    if result and st.session_state.get("result_mode") == mode:
        st.divider()
        st.subheader("Search results")
        st.caption("AI matching · source-checked evidence" if mode == "ai" else "Keyword search · not AI")
        if result.status == "matches":
            st.write("Review the original descriptions. A suggestion does not confirm ownership.")
            by_id = {r.id: r for r in catalogue}
            for index, match in enumerate(result.matches, 1):
                if match.id in by_id:
                    # The baseline quotes the complete description; repeating it adds no information.
                    item_card(by_id[match.id], index, match.evidence if mode == "ai" else None)
        elif result.status in {"error", "invalid"}:
            st.error(result.message)
        elif result.status == "refused":
            st.warning(result.message)
        else:
            st.info(result.message)
    elif not result:
        st.caption("Try the example above. The black bottle (LF-001) should appear first.")

with browse_tab:
    st.subheader("Item catalogue")
    st.caption(f"{len(catalogue)} fictional records. These are the original descriptions used in both search modes.")
    browse_category = st.selectbox("Browse by category", ["All items"] + sorted({r.type for r in catalogue}))
    visible = [r for r in catalogue if browse_category == "All items" or r.type == browse_category]
    st.caption(f"{len(visible)} items")
    for item in visible:
        item_card(item)

with about_tab:
    st.subheader("About the demonstration")
    st.write("Campus Find is an independent student project exploring lost-item matching. It is not an official HKU service.")
    st.markdown("""### How it works
The app checks an English description of up to 300 characters, searches the
selected fictional records, and returns up to three possible matches.
Keyword search counts shared words. The AI adapter requests ranked item IDs and
verbatim evidence, then rejects invalid IDs or unsupported excerpts.

### Scope and privacy
This demo cannot identify owners, reveal contacts, verify ownership or authorise
collection. It does not access real campus posts or university systems.
Queries are not saved in the database; form values and the latest result remain
in the current browser session. AI mode sends fictional input and selected
records to the configured provider, whose retention policy applies.

### Evaluation status
The keyword baseline found an acceptable item in all 10 known-match cases, but
failed all four no-match cases. These small-sample results do not measure AI
accuracy. Live AI evaluation, independent dataset review and classmate usability
checks are pending. The code and initial synthetic data were AI-assisted.
""")
    st.link_button("Read the project overview", "https://campus-find-g19-project.onrender.com")
    st.caption(f"Prompt: {PROMPT_VERSION} · Database: {engine.dialect.name} · Dataset: fictional-v1")

st.html('<footer class="app-footer">30 fictional records · Up to 3 suggestions · No ownership verification</footer>')
