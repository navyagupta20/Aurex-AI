
import streamlit as st
import pandas as pd

from database import get_sessions

st.set_page_config(page_title="Practice History | Aurex", page_icon="📚", layout="wide")

st.markdown("""
<style>
.block-container {max-width:1150px;padding-top:2rem;}
.title {font-size:34px;font-weight:800;color:#171717;}
.subtitle {color:#77716D;margin-bottom:22px;}
.history-card {
    background:#FFFFFF;border:1px solid #E8E1E1;
    border-radius:14px;padding:20px;margin-bottom:14px;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to view practice history.")
    st.stop()

user = st.session_state.get("user", {})
student_name = user.get("full_name", "Student")

st.markdown('<div class="title">Practice History</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Review previous discussions, scores, and AI feedback.</div>', unsafe_allow_html=True)

try:
    sessions = get_sessions(student_name=student_name)
except Exception as error:
    st.error(f"Could not load practice history: {error}")
    st.stop()

if not sessions:
    st.info("Your saved practice sessions will appear here.")
    st.stop()

df = pd.DataFrame(sessions)

if "mode" in df.columns:
    modes = ["All"] + sorted(df["mode"].dropna().astype(str).unique().tolist())
    selected_mode = st.selectbox("Filter by practice type", modes)
    if selected_mode != "All":
        df = df[df["mode"] == selected_mode]

if df.empty:
    st.info("No sessions match this filter.")
    st.stop()

st.caption(f"{len(df)} session(s) found")

for _, row in df.iterrows():
    topic = str(row.get("topic", "Untitled topic"))
    mode = str(row.get("mode", "Practice"))
    score = row.get("score", 0)
    created_at = row.get("created_at", "Date unavailable")
    feedback = str(row.get("feedback", "No feedback saved for this session."))

    with st.expander(f"{topic} · {mode}"):
        c1, c2 = st.columns(2)
        c1.metric("Score", f"{score}/100")
        c2.write(f"**Date:** {created_at}")
        st.markdown("**AI feedback**")
        st.write(feedback)
