"""Streamlit frontend application."""

import streamlit as st
import httpx
import json

API_BASE = "http://localhost:8000"


st.set_page_config(page_title="MCI-v2.0", page_icon="🎬", layout="wide")

st.title("MCI-v2.0: Media Content Intelligence")


def search_clips(query: str, max_results: int = 10):
    """Search for clips."""
    try:
        response = httpx.post(
            f"{API_BASE}/search",
            json={"query": query, "max_results": max_results},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Search failed: {e}")
        return None


with st.sidebar:
    st.header("Search Settings")
    max_results = st.slider("Max Results", 1, 50, 10)

    st.divider()
    show_inset = st.checkbox(
        "Show video previews (inset)",
        value=True,
        help="Embed a playable video preview for each relevant clip.",
    )

    st.divider()
    st.header("Example Queries")
    examples = [
        "Find 30-second clips where Messi is drinking from a Pepsi bottle",
        "Search for goals with Adidas logo visible",
        "Find clips cleared for Germany digital highlights",
    ]
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.query = ex


if "query" not in st.session_state:
    st.session_state.query = ""


query = st.text_input(
    "Enter your search query:",
    value=st.session_state.query,
    placeholder="e.g., Find clips where Messi drinks from a Pepsi bottle",
)


if st.button("Search", type="primary"):
    if query:
        with st.spinner("Searching..."):
            result = search_clips(query, max_results)

            if result:
                st.session_state.last_result = result
                st.session_state.query = query


if "last_result" in st.session_state:
    result = st.session_state.last_result

    st.divider()
    st.subheader(f"Results for: {result.get('query', '')}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Found", result.get("total_found", 0))
    with col2:
        st.metric("Processing Time", f"{result.get('processing_time_ms', 0):.0f}ms")
    with col3:
        review_required = result.get("human_review_required", False)
        st.metric("Human Review", "Required" if review_required else "Not Required")

    st.subheader("Candidate Clips")

    for i, clip in enumerate(result.get("candidate_clips", []), 1):
        title = clip.get("title") or clip.get("clip_id", "unknown")
        with st.expander(f"Clip {i}: {title}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Video ID:** {clip.get('video_id', 'N/A')}")
                st.write(f"**Score:** {clip.get('score', 0):.3f}")
                st.write(f"**Dataset:** {clip.get('dataset', 'N/A')}")
            with col2:
                st.write(f"**Time:** {clip.get('start_time', 0):.1f}s - {clip.get('end_time', 0):.1f}s")
                st.write(f"**Source:** {clip.get('source', 'N/A')}")

            st.write(f"**Relevance:** {clip.get('relevance_reason', 'N/A')}")
            if clip.get("asset_name"):
                st.write(f"**Original asset:** {clip['asset_name']}")

            link_col1, link_col2 = st.columns(2)
            with link_col1:
                if clip.get("source_url"):
                    st.link_button("Open exact source file", clip["source_url"])
            with link_col2:
                if clip.get("source_page"):
                    st.link_button("Open source item page", clip["source_page"])

            if show_inset:
                video_id = clip.get("video_id", "")
                if video_id:
                    video_url = f"{API_BASE}/videos/{video_id}"
                    try:
                        st.video(video_url, format=clip.get("mime_type") or "video/mp4")
                        st.caption(f"Inset preview: `{video_id}`")
                    except Exception as e:
                        st.warning(f"Unable to load video preview: {e}")
                else:
                    st.info("No video preview available for this clip.")

            if clip.get("evidence"):
                with st.expander("Evidence Details"):
                    st.json(clip.get("evidence", {}))

            if clip.get("annotations"):
                with st.expander("Dataset Annotations"):
                    st.json(clip.get("annotations", {}))

    st.divider()

    st.subheader("Feedback")
    col1, col2 = st.columns(2)
    with col1:
        feedback_clip = st.selectbox(
            "Select clip to feedback",
            [c.get("clip_id", "") for c in result.get("candidate_clips", [])],
        )
    with col2:
        feedback_type = st.radio("Feedback", ["thumbs_up", "thumbs_down"])

    if st.button("Submit Feedback"):
        try:
            httpx.post(
                f"{API_BASE}/feedback",
                json={
                    "query": query,
                    "clip_id": feedback_clip,
                    "feedback": feedback_type,
                },
            )
            st.success("Feedback submitted!")
        except Exception as e:
            st.error(f"Feedback failed: {e}")


st.divider()
st.caption("MCI-v2.0 Media Content Intelligence Platform")
