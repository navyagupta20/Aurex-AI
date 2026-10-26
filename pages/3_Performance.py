
import streamlit as st
import pandas as pd
import json

from database import get_sessions

st.set_page_config(page_title="Performance | Aurex", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {max-width:1150px;padding-top:2rem;}
.title {font-size:34px;font-weight:800;color:#171717;}
.subtitle {color:#77716D;margin-bottom:22px;}
div[data-testid="stMetric"] {
    background:#FFFFFF;border:1px solid #E8E1E1;
    padding:18px;border-radius:14px;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to view performance.")
    st.stop()

user = st.session_state.get("user", {})
student_name = user.get("full_name", "Student")

st.markdown('<div class="title">Your Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Track your practice activity and improvement over time.</div>', unsafe_allow_html=True)

try:
    sessions = get_sessions(student_name=student_name)
except Exception as error:
    st.error(f"Could not load performance data: {error}")
    st.stop()

if not sessions:
    st.info("No practice sessions saved yet. Complete a Topic Practice or Live GD Challenge to see your progress.")
    st.stop()

df = pd.DataFrame(sessions)

if "score" not in df.columns:
    df["score"] = 0

df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)

total_sessions = len(df)
average_score = round(df["score"].mean(), 1)
best_score = round(df["score"].max(), 1)

c1, c2, c3 = st.columns(3)
c1.metric("Sessions completed", total_sessions)
c2.metric("Average score", f"{average_score}/100")
c3.metric("Best score", f"{best_score}/100")

st.markdown("### Score overview")
if "topic" in df.columns:
    chart_df = df[["topic", "score"]].copy()
    chart_df["Topic"] = chart_df["topic"].astype(str).str.slice(0, 35)
    st.bar_chart(chart_df.set_index("Topic")["score"])

st.markdown("### Recent sessions")
display_columns = [
    column for column in ["topic", "mode", "score", "created_at"]
    if column in df.columns
]
st.dataframe(df[display_columns], use_container_width=True, hide_index=True)

st.markdown("### Category scores")
all_scores = []

for _, row in df.iterrows():
    raw = row.get("scores", row.get("scores_json", "{}"))
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            raw = {}

    if isinstance(raw, dict):
        for field in ["relevance", "clarity", "reasoning", "examples", "engagement"]:
            if field in raw:
                all_scores.append({
                    "Category": field.title(),
                    "Score": raw[field],
                })

if all_scores:
    category_df = pd.DataFrame(all_scores)
    category_summary = category_df.groupby("Category", as_index=False)["Score"].mean()
    st.bar_chart(category_summary.set_index("Category")["Score"])
else:
    st.caption("Category-level scores will appear after saving AI feedback.")
