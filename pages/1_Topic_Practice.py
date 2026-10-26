
import streamlit as st

from ai_coach import TOPICS, evaluate_discussion, generate_topic
from database import save_session


st.set_page_config(
    page_title="Topic Practice | Aurex",
    page_icon="🎯",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .page-title {
        color: #171717;
        font-size: 34px;
        font-weight: 800;
    }
    .page-subtitle {
        color: #77716D;
        margin-bottom: 24px;
    }
    div.stButton > button[kind="primary"] {
        background: #8F2945;
        color: white;
        border: none;
        border-radius: 9px;
        min-height: 44px;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #702037;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access Topic Practice.")
    st.stop()

user = st.session_state.get("user", {})
student_name = user.get("full_name", "Student")

st.markdown(
    '<div class="page-title">Topic-Based GD Practice</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-subtitle">'
    'Practise expressing your ideas and receive personalized AI feedback.'
    '</div>',
    unsafe_allow_html=True,
)

difficulty = st.selectbox(
    "Choose difficulty",
    ["Beginner", "Intermediate", "Advanced"],
)

topic_options = TOPICS[difficulty]

topic_choice = st.selectbox(
    "Choose a discussion topic",
    topic_options,
)

if st.button("Generate a new AI topic"):
    try:
        st.session_state["generated_practice_topic"] = generate_topic(
            difficulty
        )
        st.rerun()
    except Exception as error:
        st.error(f"Could not generate a topic: {error}")

topic = st.session_state.get("generated_practice_topic", topic_choice)

st.markdown("### Your discussion topic")
st.info(topic)

if st.button("Use selected topic"):
    st.session_state["generated_practice_topic"] = topic_choice
    st.rerun()

st.markdown("### Share your viewpoint")

answer = st.text_area(
    "Your opening statement",
    height=220,
    placeholder=(
        "State your opinion, explain your reasons, and support your "
        "argument with a relevant example..."
    ),
)

st.caption(f"{len(answer.split())} words")

if st.button("Evaluate my response", type="primary"):
    if len(answer.split()) < 20:
        st.warning("Please write at least 20 words before requesting feedback.")
    else:
        conversation = [
            {"role": "user", "content": answer.strip()}
        ]

        try:
            with st.spinner("Aurex AI is evaluating your response..."):
                feedback = evaluate_discussion(topic, conversation)

            st.session_state["topic_practice_feedback"] = {
                "topic": topic,
                "difficulty": difficulty,
                "answer": answer.strip(),
                "feedback": feedback,
            }

        except Exception as error:
            st.error("AI evaluation failed.")
            st.exception(error)

result = st.session_state.get("topic_practice_feedback")

if result:
    feedback = result["feedback"]

    st.markdown("---")
    st.markdown("### Your AI performance report")

    score_columns = st.columns(3)

    score_fields = [
        ("Overall score", "overall_score"),
        ("Relevance", "relevance"),
        ("Clarity", "clarity"),
        ("Reasoning", "reasoning"),
        ("Examples", "examples"),
        ("Engagement", "engagement"),
    ]

    for index, (label, field) in enumerate(score_fields):
        with score_columns[index % 3]:
            st.metric(label, f"{feedback[field]}/100")

    st.markdown("#### What you did well")
    for item in feedback["strengths"]:
        st.write(f"✓ {item}")

    st.markdown("#### What to improve")
    for item in feedback["improvements"]:
        st.write(f"• {item}")

    st.markdown("#### Coach's feedback")
    st.write(feedback["feedback"])

    st.markdown("#### Your next step")
    st.info(feedback["next_step"])

    if st.button("Save practice session"):
        try:
            save_session(
                student_name=student_name,
                mode="Topic Practice",
                topic=result["topic"],
                score=feedback["overall_score"],
                scores_json=__import__("json").dumps(feedback),
                feedback=feedback["feedback"],
            )
            st.success("Your practice session has been saved.")
        except Exception as error:
            st.error("Could not save your practice session.")
            st.exception(error)
