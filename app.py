import streamlit as st
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.styles import SPOTIFY_CSS
from ui.components import (
    render_last_run_highlights,
    render_filter_stats,
    render_opportunity_chart,
    render_hypothesis_card,
    render_segment_cards,
    render_qa_answer,
)
from pipeline.storage import init_db, get_last_run
from rag.qa_chain import PREDEFINED_QUESTIONS, ask

init_db()

st.set_page_config(
    page_title="Spotify Review Analyser",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(SPOTIFY_CSS, unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "show_full_run" not in st.session_state:
    st.session_state.show_full_run = False
if "qa_result" not in st.session_state:
    st.session_state.qa_result = None
if "qa_question" not in st.session_state:
    st.session_state.qa_question = ""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎵 Spotify Review Analyser")
    st.markdown("---")

    st.markdown("### Sources")
    src_app_store = st.checkbox("App Store", value=True)
    src_play_store = st.checkbox("Play Store", value=True)
    src_community = st.checkbox("Spotify Community", value=True)

    st.markdown("### Timeline")
    timeline = st.selectbox(
        "Review period",
        options=[7, 30, 90],
        index=1,
        format_func=lambda x: f"Last {x} days",
    )

    st.markdown("---")

    last_run = get_last_run()
    if last_run:
        st.markdown("### Last Run")
        st.markdown(f"📅 {last_run.get('completed_at', '')[:10]}")
        st.markdown(f"📊 {last_run.get('total_clean', 0):,} reviews")

    st.markdown("---")
    st.markdown(
        "<div style='color:#B3B3B3; font-size:0.75rem;'>Powered by Groq + Claude + ChromaDB</div>",
        unsafe_allow_html=True,
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1>🎵 Spotify <span class='green'>Review Analysis</span> Engine</h1>",
    unsafe_allow_html=True,
)
st.markdown("<p style='color:#B3B3B3;'>AI-powered opportunity discovery from user feedback at scale.</p>",
            unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["▶  Run Analysis", "📊  Dashboard", "💬  Ask a Question"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Run Analysis
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Last run highlights
    result_to_show = st.session_state.last_result or last_run
    render_last_run_highlights(result_to_show)

    if result_to_show and result_to_show.get("clusters"):
        if st.button("📋 View Full Last Run", key="view_full"):
            st.session_state.show_full_run = not st.session_state.show_full_run

        if st.session_state.show_full_run:
            st.markdown("---")
            st.markdown("### Full Last Run Results")

            filter_log = result_to_show.get("filter_log", {})
            if filter_log:
                render_filter_stats(filter_log)

            st.markdown("#### Opportunity Clusters")
            for cluster in result_to_show.get("clusters", []):
                render_hypothesis_card(cluster)

            digest = result_to_show.get("digest", "")
            if digest:
                st.markdown("#### Executive Digest")
                st.markdown(f"""
                <div class="spotify-card">
                    {digest}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Run New Analysis")

    selected_sources = []
    if src_app_store:
        selected_sources.append("app_store")
    if src_play_store:
        selected_sources.append("play_store")
    if src_community:
        selected_sources.append("community")

    if not selected_sources:
        st.warning("Select at least one source in the sidebar.")
    else:
        st.markdown(
            f"<p style='color:#B3B3B3;'>Will scrape <strong style='color:#1DB954;'>"
            f"{', '.join(selected_sources)}</strong> for the last "
            f"<strong style='color:#1DB954;'>{timeline} days</strong>.</p>",
            unsafe_allow_html=True,
        )

        if st.button("▶  Run Analysis", type="primary", key="run_btn"):
            from pipeline.runner import run_pipeline

            progress_bar = st.progress(0)
            status_area = st.empty()
            steps = {
                "scraping_app_store": (5, "🔄 Scraping App Store..."),
                "scraping_play_store": (15, "🔄 Scraping Play Store..."),
                "scraping_community": (25, "🔄 Scraping Spotify Community..."),
                "filtering": (35, "🔍 Filtering reviews..."),
                "extracting": (45, "🤖 Running Groq AI extraction..."),
                "scoring": (70, "📊 Scoring opportunities..."),
                "synthesizing": (80, "✨ Generating insights with Claude..."),
                "indexing_rag": (92, "🔗 Building RAG index..."),
            }

            progress_pct = [0]

            def on_progress(msg: str):
                for key, (pct, label) in steps.items():
                    if msg.startswith(key):
                        progress_pct[0] = pct
                        progress_bar.progress(pct)
                        status_area.markdown(
                            f"<div style='color:#1DB954;'>{label}</div>",
                            unsafe_allow_html=True,
                        )
                        return
                if msg.startswith("groq_batch:"):
                    parts = msg.split(":")[1].split("/")
                    done, total = int(parts[0]), int(parts[1])
                    pct = 45 + int((done / total) * 25)
                    progress_bar.progress(pct)
                    status_area.markdown(
                        f"<div style='color:#1DB954;'>🤖 Groq extraction: batch {done}/{total}</div>",
                        unsafe_allow_html=True,
                    )
                elif msg.startswith("done:"):
                    progress_bar.progress(100)
                    status_area.markdown(
                        "<div style='color:#1DB954;'>✅ Analysis complete!</div>",
                        unsafe_allow_html=True,
                    )

            try:
                result = run_pipeline(
                    sources=selected_sources,
                    days=timeline,
                    progress_callback=on_progress,
                )
                st.session_state.last_result = result
                st.session_state.show_full_run = False

                st.success(
                    f"✅ Done! {result['total_clean']:,} reviews analysed · "
                    f"{len(result.get('clusters', []))} opportunity clusters found"
                )
                st.info("Switch to the **Dashboard** or **Ask a Question** tab to explore results.")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
                progress_bar.empty()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    result = st.session_state.last_result or last_run

    if not result or not result.get("clusters"):
        st.markdown(
            "<div class='spotify-card' style='text-align:center; color:#B3B3B3;'>"
            "No data yet. Run an analysis first.</div>",
            unsafe_allow_html=True,
        )
    else:
        clusters = result.get("clusters", [])
        total_clean = result.get("total_clean", 0)
        top_cluster = clusters[0] if clusters else {}

        # Metric cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Reviews Analysed", f"{total_clean:,}")
        col2.metric("Opportunity Clusters", len(clusters))
        col3.metric("Top Signal", f"{top_cluster.get('label', '—')[:20]}")

        st.markdown("---")

        # Opportunity chart
        st.markdown("### Opportunity Clusters by Signal Strength")
        render_opportunity_chart(clusters)

        st.markdown("---")

        # Segment breakdown
        st.markdown("### Who Feels It Most?")
        render_segment_cards(clusters)

        st.markdown("---")

        # Hypothesis cards
        st.markdown("### Opportunity Deep-Dives")
        st.markdown("<p style='color:#B3B3B3;'>Click a cluster to expand details, validation questions, and supporting quotes.</p>",
                    unsafe_allow_html=True)
        for cluster in clusters:
            render_hypothesis_card(cluster)

        # Digest
        digest = result.get("digest", "")
        if digest:
            st.markdown("---")
            st.markdown("### Executive Digest")
            st.markdown(f"""
            <div class="spotify-card">
                <p style="line-height:1.8;">{digest}</p>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Ask a Question
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    from rag.embedder import get_index_count
    index_count = get_index_count()

    if index_count == 0:
        st.markdown(
            "<div class='spotify-card' style='text-align:center; color:#B3B3B3;'>"
            "No reviews indexed yet. Run an analysis first to enable Q&A.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<p style='color:#B3B3B3;'>Searching across <strong style='color:#1DB954;'>"
            f"{index_count:,} reviews</strong> in the knowledge base.</p>",
            unsafe_allow_html=True,
        )

        st.markdown("### Pre-built Questions")
        st.markdown("<p style='color:#B3B3B3; font-size:0.9rem;'>Click any card to get an instant answer.</p>",
                    unsafe_allow_html=True)

        cols = st.columns(2)
        for i, question in enumerate(PREDEFINED_QUESTIONS):
            with cols[i % 2]:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    st.session_state.qa_question = question
                    with st.spinner("Searching reviews and generating answer..."):
                        st.session_state.qa_result = ask(question)

        st.markdown("---")
        st.markdown("### Ask Your Own Question")
        custom_q = st.text_input(
            "",
            placeholder="e.g. What do power users say about Discover Weekly?",
            key="custom_q",
            label_visibility="collapsed",
        )
        if st.button("Ask", key="ask_custom") and custom_q.strip():
            st.session_state.qa_question = custom_q
            with st.spinner("Searching reviews and generating answer..."):
                st.session_state.qa_result = ask(custom_q)

        # Answer
        if st.session_state.qa_result:
            st.markdown("---")
            st.markdown(f"### Answer: _{st.session_state.qa_question}_")
            render_qa_answer(st.session_state.qa_result)
