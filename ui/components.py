import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def signal_badge(score: int) -> str:
    if score >= 70:
        return f'<span class="badge-high">HIGH {score}</span>'
    elif score >= 45:
        return f'<span class="badge-medium">MED {score}</span>'
    return f'<span class="badge-low">LOW {score}</span>'


def render_last_run_highlights(last_run: dict):
    if not last_run:
        st.markdown(
            '<div class="last-run-box">No analysis run yet. Run your first analysis below.</div>',
            unsafe_allow_html=True,
        )
        return

    from datetime import datetime
    date_str = last_run.get("completed_at", "")[:10]
    total_clean = last_run.get("total_clean", 0)
    clusters = last_run.get("clusters", [])[:3]

    top_signals = " &nbsp;·&nbsp; ".join(
        f'{signal_badge(c["signal_strength"])} {c["label"]}'
        for c in clusters
    )

    st.markdown(f"""
    <div class="last-run-box">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="color:#B3B3B3; font-size:0.85rem;">LAST RUN</span><br>
                <span style="font-size:1.1rem; font-weight:600;">{date_str}</span>
                <span style="color:#B3B3B3;"> &nbsp;·&nbsp; {total_clean:,} reviews analysed</span>
            </div>
        </div>
        <div style="margin-top:0.8rem;">{top_signals}</div>
    </div>
    """, unsafe_allow_html=True)


def render_filter_stats(filter_log: dict):
    total_raw = filter_log.get("total_raw", 0)
    passed = filter_log.get("passed", 0)
    dropped = total_raw - passed

    col1, col2, col3 = st.columns(3)
    col1.metric("Scraped", f"{total_raw:,}")
    col2.metric("Filtered out", f"{dropped:,}")
    col3.metric("Analysed", f"{passed:,}")


def render_opportunity_chart(clusters: list[dict]):
    if not clusters:
        st.info("No clusters yet. Run an analysis first.")
        return

    labels = [c["label"] for c in clusters]
    scores = [c["signal_strength"] for c in clusters]
    colors = ["#1DB954" if s >= 70 else "#F59B23" if s >= 45 else "#535353" for s in scores]

    fig = go.Figure(go.Bar(
        x=scores,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{s}/100" for s in scores],
        textposition="outside",
        textfont=dict(color="#FFFFFF"),
    ))
    fig.update_layout(
        paper_bgcolor="#191414",
        plot_bgcolor="#191414",
        font=dict(color="#FFFFFF"),
        xaxis=dict(range=[0, 110], showgrid=False, color="#B3B3B3"),
        yaxis=dict(autorange="reversed", color="#FFFFFF"),
        margin=dict(l=10, r=60, t=10, b=10),
        height=50 + len(clusters) * 52,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_hypothesis_card(cluster: dict):
    hypothesis = cluster.get("hypothesis") or {}
    label = cluster.get("label", "")
    score = cluster.get("signal_strength", 0)
    count = cluster.get("count", 0)
    segment = cluster.get("top_segment", "unknown")
    frustrations = cluster.get("top_frustrations", [])

    badge = signal_badge(score)
    hyp_text = hypothesis.get("hypothesis", "") if hypothesis else ""
    opportunity = hypothesis.get("opportunity", "") if hypothesis else ""
    val_questions = hypothesis.get("validation_questions", []) if hypothesis else []

    with st.expander(f"{'🔴' if score >= 70 else '🟠' if score >= 45 else '🟡'} {label}  —  {count} reviews", expanded=score >= 70):
        st.markdown(f"{badge} &nbsp; Top segment: **{segment}**", unsafe_allow_html=True)

        if frustrations:
            st.markdown("**Top frustrations:** " + " · ".join(f"`{f}`" for f in frustrations))

        if hyp_text:
            st.markdown(f"**Problem:** {hyp_text}")
        if opportunity:
            st.markdown(f"**Opportunity:** _{opportunity}_")

        if val_questions:
            st.markdown("**Interview questions to validate:**")
            for q in val_questions:
                st.markdown(f"- {q}")

        quotes = cluster.get("key_quotes", [])
        if quotes:
            st.markdown("**Supporting quotes:**")
            for q in quotes[:3]:
                source = q.get("source", "")
                date = q.get("date", "")[:10] if q.get("date") else ""
                rating = q.get("rating")
                stars = "★" * int(rating) if rating and str(rating).isdigit() else ""
                st.markdown(f"""
                <div class="quote-card">
                    "{q.get('quote', '')}"
                    <div class="quote-meta">{source} · {date} {stars}</div>
                </div>
                """, unsafe_allow_html=True)


def render_segment_cards(clusters: list[dict]):
    if not clusters:
        return

    segment_data = {}
    for c in clusters:
        for seg, count in c.get("segment_breakdown", {}).items():
            if seg not in segment_data:
                segment_data[seg] = {"count": 0, "top_issue": ""}
            segment_data[seg]["count"] += count
            if not segment_data[seg]["top_issue"] and c.get("top_frustrations"):
                segment_data[seg]["top_issue"] = c["top_frustrations"][0]

    labels = {"casual": "Casual Listeners", "power_user": "Power Users",
              "audiophile": "Audiophiles", "unknown": "Unknown"}

    cols = st.columns(min(len(segment_data), 3))
    for i, (seg, data) in enumerate(segment_data.items()):
        if i >= 3:
            break
        with cols[i]:
            st.markdown(f"""
            <div class="spotify-card" style="text-align:center;">
                <div style="color:#1DB954; font-weight:700; font-size:1.1rem;">{labels.get(seg, seg)}</div>
                <div style="color:#B3B3B3; font-size:0.85rem; margin:0.3rem 0;">Top issue:</div>
                <div style="font-size:0.9rem;">{data['top_issue'] or '—'}</div>
                <div style="color:#1DB954; margin-top:0.5rem; font-size:1.3rem; font-weight:700;">{data['count']}</div>
                <div style="color:#B3B3B3; font-size:0.75rem;">mentions</div>
            </div>
            """, unsafe_allow_html=True)


def render_qa_answer(result: dict):
    if not result:
        return

    signal = result.get("signal_strength_pct", 0)
    st.markdown(f"""
    <div class="spotify-card">
        <div style="color:#1DB954; font-weight:700; margin-bottom:0.5rem;">
            Signal strength: {signal}%
        </div>
        <div style="font-size:1rem; line-height:1.6;">{result.get('answer', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    patterns = result.get("key_patterns", [])
    if patterns:
        st.markdown("**Key patterns:**")
        for p in patterns:
            st.markdown(f"- {p}")

    quotes = result.get("supporting_quotes", [])
    if quotes:
        st.markdown("**Supporting quotes:**")
        for q in quotes:
            source = q.get("source", "")
            date = q.get("date", "")[:10] if q.get("date") else ""
            rating = q.get("rating", "")
            stars = "★" * int(rating) if rating and str(rating).isdigit() else ""
            st.markdown(f"""
            <div class="quote-card">
                "{q.get('quote', '')}"
                <div class="quote-meta">{source} · {date} {stars}</div>
            </div>
            """, unsafe_allow_html=True)

    opportunity = result.get("opportunity_hypothesis", "")
    if opportunity:
        st.markdown(f"""
        <div class="spotify-card" style="border-color:#1DB954; margin-top:1rem;">
            💡 <strong>Opportunity hypothesis:</strong><br>{opportunity}
        </div>
        """, unsafe_allow_html=True)
