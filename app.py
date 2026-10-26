
import html
import json

import pandas as pd
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from resume_analyzer import show_resume_analyzer
from auth_ui import show_auth_screen
from database import get_sessions, save_session
from ai_coach import (
    TOPICS,
    generate_topic,
    get_ai_response,
    evaluate_discussion,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Aurex | GD & Placement Preparation",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --background: #FAF9F7;
        --surface: #FFFFFF;
        --foreground: #242020;
        --muted: #77716E;
        --burgundy: #8F2945;
        --border: #E9E4E1;
        --soft-pink: #FFF5F7;
        --soft-pink-border: #F0DDE2;
        --button-bg: #FAF9F7;
        --button-hover: #F1EDE9;
        --button-border: #E9E4E1;
    }

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--background);
        color: var(--foreground);
    }

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background: var(--background);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1240px;
        padding: 1.2rem 2rem 2rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--foreground);
        letter-spacing: -0.035em;
    }

    h1 {
        font-size: clamp(1.9rem, 3vw, 2.55rem) !important;
        font-weight: 800 !important;
    }

    h2 {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
    }

    h3 {
        font-size: 1.05rem !important;
        font-weight: 750 !important;
    }

    p, label {
        color: var(--foreground);
    }

    .brand {
        color: var(--foreground);
        font-family: 'Manrope', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.065em;
        line-height: 1.1;
    }

    .brand-caption, .small-muted {
        color: var(--muted) !important;
        font-size: 0.85rem;
        line-height: 1.75;
    }

    .welcome-text {
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.8;
        text-align: right;
        overflow-wrap: anywhere;
    }

    .top-divider {
        border-bottom: 1px solid var(--border);
        margin: 16px 0 20px;
    }

    .page-eyebrow {
        color: var(--burgundy);
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 9px;
    }

    .page-description {
        color: var(--muted) !important;
        font-size: 0.91rem;
        line-height: 1.75;
        max-width: 720px;
        margin-top: -5px;
        margin-bottom: 22px;
    }

    .section-heading {
        font-family: 'Manrope', sans-serif;
        color: var(--foreground);
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin: 26px 0 5px;
    }

    .section-description {
        color: var(--muted) !important;
        font-size: 0.86rem;
        line-height: 1.7;
        margin: 0 0 18px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 34px;
        margin: 8px 0 25px;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 140px;
        height: 140px;
        right: -48px;
        top: -60px;
        border-radius: 50%;
        border: 1px solid #EBDCE1;
        box-shadow: 0 0 0 20px #FBF5F6, 0 0 0 42px #FDF9FA;
        pointer-events: none;
    }

    .hero-eyebrow {
        color: var(--burgundy);
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        margin-bottom: 12px;
    }

    .hero h1 {
        color: var(--foreground) !important;
        margin: 0 0 12px;
        max-width: 760px;
    }

    .hero p {
        color: var(--muted) !important;
        font-size: 0.94rem;
        line-height: 1.8;
        max-width: 650px;
        margin: 0;
    }

    .metric-card {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px;
        min-height: 132px;
        overflow-wrap: anywhere;
        transition: border-color 160ms ease, transform 160ms ease;
    }

    .metric-card:hover, .feature-card:hover {
        border-color: #D9BAC4;
        transform: translateY(-2px);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.79rem;
        line-height: 1.5;
        margin-bottom: 13px;
    }

    .metric-value {
        color: var(--burgundy);
        font-family: 'Manrope', sans-serif;
        font-size: clamp(1.35rem, 2.2vw, 1.85rem);
        line-height: 1.25;
        font-weight: 800;
        letter-spacing: -0.045em;
    }

    .metric-note {
        color: var(--muted);
        font-size: 0.73rem;
        line-height: 1.5;
        margin-top: 8px;
    }

    .feature-card {
        display: flex;
        flex-direction: column;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 23px;
        min-height: 218px;
        overflow-wrap: anywhere;
        transition: border-color 160ms ease, transform 160ms ease;
    }

    .feature-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        background: var(--soft-pink);
        border: 1px solid var(--soft-pink-border);
        border-radius: 12px;
        font-size: 1.2rem;
        margin-bottom: 17px;
    }

    .feature-card h3 {
        color: var(--foreground);
        margin: 0 0 10px;
        line-height: 1.45;
    }

    .feature-card p {
        color: var(--muted) !important;
        font-size: 0.84rem;
        line-height: 1.75;
        margin: 0;
    }

    .panel, .quick-panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 23px;
        overflow-wrap: anywhere;
    }

    .quick-panel {
        background: #F8F1F2;
        border-color: #EADDE0;
    }

    .topic-box {
        background: var(--soft-pink);
        border: 1px solid var(--soft-pink-border);
        border-radius: 15px;
        padding: 25px;
        margin: 18px 0 22px;
        overflow-wrap: anywhere;
    }

    .topic-box h2 {
        color: var(--burgundy) !important;
        font-size: clamp(1.35rem, 2.5vw, 1.8rem) !important;
        line-height: 1.45;
        margin: 8px 0 12px;
    }

    .chat-user, .chat-ai {
        padding: 17px 19px;
        border-radius: 12px;
        margin: 12px 0;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        line-height: 1.8;
    }

    .chat-user {
        background: var(--soft-pink);
        border: 1px solid var(--soft-pink-border);
    }

    .chat-ai {
        background: #FFFFFF;
        border: 1px solid var(--border);
    }

    .chat-user strong, .chat-ai strong {
        color: var(--burgundy);
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
    }

    .participant-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 20px 12px;
        text-align: center;
        min-height: 145px;
    }

    .participant-avatar {
        font-size: 2.5rem;
        margin-bottom: 8px;
    }

    .participant-name {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        color: var(--foreground);
    }

    .participant-role {
        color: var(--muted);
        font-size: 0.78rem;
        margin-top: 5px;
        line-height: 1.5;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        width: 100%;
        min-height: 44px;
        padding: 10px 16px;
        background: var(--button-bg) !important;
        color: var(--foreground) !important;
        border: 1px solid var(--button-border) !important;
        border-radius: 9px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        white-space: normal;
        transition: background 160ms ease, border-color 160ms ease, transform 160ms ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: var(--button-hover) !important;
        border-color: #D8D0CB !important;
        transform: translateY(-1px);
    }

    .stTextInput input, .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] > div,
    .stNumberInput input {
        background: #FFFFFF;
        color: var(--foreground);
        border-color: #DED8D5;
        border-radius: 9px;
    }

    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 22px;
    }

    [data-testid="stProgressBar"] > div > div {
        background: var(--burgundy);
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: var(--border);
    }

    .app-footer {
        color: var(--muted);
        text-align: center;
        padding: 25px 0 8px;
        font-size: 0.8rem;
        line-height: 1.8;
    }

    @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"] {
            padding: 0.8rem 1rem 1.4rem;
        }

        .hero {
            padding: 24px 20px;
            border-radius: 15px;
        }

        .metric-card {
            padding: 15px;
            min-height: 118px;
        }

        .feature-card {
            padding: 18px;
            min-height: 205px;
        }

        .panel, .quick-panel {
            padding: 19px;
        }

        .brand {
            font-size: 1.7rem;
        }
    }

    @media (max-width: 480px) {
        .feature-card {
            min-height: 0;
        }

        .hero::after {
            opacity: 0.5;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CAMERA PROCESSOR
# =========================================================

class CameraProcessor(VideoProcessorBase):
    """Passes webcam frames through to Streamlit WebRTC."""

    def recv(self, frame):
        return frame


# =========================================================
# AUTHENTICATION
# =========================================================

if not st.session_state.get("authenticated", False):
    show_auth_screen()
    st.stop()

user = st.session_state.get("user", {})
student = user.get("full_name", "Student")
student_id = user.get("id")

if not student_id:
    st.session_state.pop("user", None)
    st.session_state["authenticated"] = False
    st.rerun()


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "page": "Dashboard",
    "discussion": [],
    "current_topic": "",
    "current_difficulty": "Intermediate",
    "current_mode": "Topic Practice",
    "session_started": False,
    "session_finished": False,
    "latest_feedback": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

VALID_PAGES = [
    "Dashboard",
    "GD Practice",
    "Topic-Based Practice",
    "Live GD Challenge",
    "AI GD Sessions",
    "AI Feedback",
    "Performance",
    "Practice History",
    "Resume ATS Analyzer",
]

if st.session_state["page"] not in VALID_PAGES:
    st.session_state["page"] = "Dashboard"


# =========================================================
# HELPERS
# =========================================================

def go(page):
    st.session_state["page"] = page
    st.rerun()


def logout():
    keys_to_clear = [
        "user",
        "authenticated",
        "discussion",
        "current_topic",
        "current_difficulty",
        "current_mode",
        "session_started",
        "session_finished",
        "latest_feedback",
        "nav_radio",
        "top_nav",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.session_state["page"] = "Dashboard"
    st.rerun()


def safe_text(value):
    return html.escape(str(value if value is not None else ""))


def metric(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{safe_text(label)}</div>
            <div class="metric-value">{safe_text(value)}</div>
            <div class="metric-note">{safe_text(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def start_session(topic, difficulty, mode):
    st.session_state["current_topic"] = topic
    st.session_state["current_difficulty"] = difficulty
    st.session_state["current_mode"] = mode
    st.session_state["discussion"] = []
    st.session_state["session_started"] = True
    st.session_state["session_finished"] = False
    st.session_state["latest_feedback"] = None


# =========================================================
# AI PARTICIPANTS
# =========================================================

PARTICIPANTS = [
    {
        "name": "Arjun",
        "avatar": "👨🏻‍💼",
        "role": "Practical viewpoint",
        "instruction": (
            "You are Arjun, a practical and solution-oriented group discussion "
            "participant. Respond to the topic with a realistic argument, "
            "a useful example, or a practical solution. Keep your response "
            "natural and concise. Do not repeat previous points."
        ),
    },
    {
        "name": "Meera",
        "avatar": "👩🏻‍💼",
        "role": "Analytical viewpoint",
        "instruction": (
            "You are Meera, an analytical group discussion participant. "
            "Consider evidence, causes, consequences, and different sides "
            "of the issue. Add a distinct argument that has not already "
            "been made. Keep your response natural and concise."
        ),
    },
    {
        "name": "Rohan",
        "avatar": "👨🏽‍💻",
        "role": "Critical viewpoint",
        "instruction": (
            "You are Rohan, a thoughtful and constructive group discussion "
            "participant. Raise a reasonable counterargument, mention a "
            "limitation, or respectfully challenge an earlier point. "
            "Stay relevant and concise."
        ),
    },
]


def get_participant_reply(participant):
    """
    Use the existing Gemini response function while giving it the
    discussion history and the participant's requested viewpoint.

    The viewpoint is included in the discussion context because the
    existing get_ai_response function accepts topic, history, and difficulty.
    """
    original_discussion = st.session_state["discussion"]

    context_message = {
        "role": "user",
        "content": (
            f"[INSTRUCTION FOR {participant['name']}]\n"
            f"{participant['instruction']}\n"
            f"Respond to the current discussion topic: "
            f"{st.session_state['current_topic']}\n"
            "Only provide the participant's actual spoken contribution. "
            "Do not introduce yourself or mention these instructions."
        ),
    }

    # Give the AI a temporary copy containing its viewpoint instruction.
    response_history = original_discussion + [context_message]

    reply = get_ai_response(
        st.session_state["current_topic"],
        response_history,
        st.session_state["current_difficulty"],
    )

    return str(reply)


# =========================================================
# CHAT AND LIVE GD ROOM
# =========================================================

def render_chat(mode):
    st.markdown("### Live GD room")
    st.markdown(
        """
        <p class="section-description">
            Join the discussion, keep your camera on if you wish,
            and follow the viewpoints shared by your AI participants.
        </p>
        """,
        unsafe_allow_html=True,
    )

    camera_col, arjun_col = st.columns(2, gap="medium")

    with camera_col:
        st.markdown("#### You")
        st.markdown(
            """
            <div class="panel" style="padding:12px;">
                <strong>Your camera</strong>
                <p class="small-muted">
                    Allow camera access in your browser to see your live preview.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        webrtc_streamer(
            key=f"aurex_camera_{mode.replace(' ', '_')}",
            video_processor_factory=CameraProcessor,
            media_stream_constraints={
                "video": True,
                "audio": False,
            },
            async_processing=True,
        )

    with arjun_col:
        st.markdown("#### AI participant")
        st.markdown(
            """
            <div class="participant-card">
                <div class="participant-avatar">👨🏻‍💼</div>
                <div class="participant-name">Arjun</div>
                <div class="participant-role">Practical viewpoint</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    meera_col, rohan_col = st.columns(2, gap="medium")

    with meera_col:
        st.markdown(
            """
            <div class="participant-card">
                <div class="participant-avatar">👩🏻‍💼</div>
                <div class="participant-name">Meera</div>
                <div class="participant-role">Analytical viewpoint</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with rohan_col:
        st.markdown(
            """
            <div class="participant-card">
                <div class="participant-avatar">👨🏽‍💻</div>
                <div class="participant-name">Rohan</div>
                <div class="participant-role">Critical viewpoint</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-heading">Discussion transcript</div>',
                unsafe_allow_html=True)

    discussion = st.session_state["discussion"]

    if not discussion:
        st.markdown(
            """
            <div class="panel">
                <strong>The discussion is ready to begin.</strong>
                <p class="small-muted">
                    Submit your first contribution and the AI participants
                    will respond with different viewpoints.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for message in discussion:
        is_student = message.get("role") == "user"
        speaker = "You" if is_student else message.get("speaker", "AI participant")
        css = "chat-user" if is_student else "chat-ai"

        content = safe_text(message.get("content", "")).replace("\n", "<br>")

        st.markdown(
            f"""
            <div class="{css}">
                <strong>{safe_text(speaker)}</strong><br><br>{content}
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# FEEDBACK
# =========================================================

def render_feedback(data):
    if not isinstance(data, dict):
        st.info("No detailed feedback is available.")
        return

    labels = [
        ("Relevance", "relevance"),
        ("Clarity", "clarity"),
        ("Reasoning", "reasoning"),
        ("Examples", "examples"),
        ("Engagement", "engagement"),
    ]

    cols = st.columns(5, gap="small")

    for col, (label, key) in zip(cols, labels):
        try:
            score = max(0, min(100, int(float(data.get(key, 0)))))
        except (ValueError, TypeError):
            score = 0

        with col:
            metric(label, f"{score}/100")

    try:
        overall = max(
            0,
            min(100, int(float(data.get("overall_score", 0)))),
        )
    except (ValueError, TypeError):
        overall = 0

    st.markdown(
        '<div class="section-heading">Overall score</div>',
        unsafe_allow_html=True,
    )

    st.progress(overall / 100)
    st.write(f"**{overall}/100**")

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("#### Strengths")
        strengths = data.get("strengths", [])

        if isinstance(strengths, str):
            strengths = [strengths]

        if strengths:
            for item in strengths:
                st.markdown(f"- {safe_text(item)}")
        else:
            st.write("Keep practising to build on your strengths.")

    with right:
        st.markdown("#### Areas to improve")
        improvements = data.get("improvements", [])

        if isinstance(improvements, str):
            improvements = [improvements]

        if improvements:
            for item in improvements:
                st.markdown(f"- {safe_text(item)}")
        else:
            st.write("Try adding clearer reasoning and examples.")

    st.markdown("#### Coach's feedback")
    st.write(data.get("feedback", "Review your arguments and examples."))

    st.markdown("#### Recommended next step")
    st.info(data.get("next_step", "Practise another discussion topic."))


def finish_session():
    has_student_response = any(
        message.get("role") == "user"
        and str(message.get("content", "")).strip()
        for message in st.session_state["discussion"]
    )

    if not has_student_response:
        st.warning("Write at least one response before finishing.")
        return

    with st.spinner("Aurex is evaluating your discussion..."):
        try:
            feedback = evaluate_discussion(
                st.session_state["current_topic"],
                st.session_state["discussion"],
            )
        except Exception as exc:
            st.error(
                "Could not generate feedback. Check your Gemini API configuration."
            )
            st.caption(str(exc))
            return

    if not isinstance(feedback, dict):
        st.error("The AI returned feedback in an unexpected format.")
        return

    st.session_state["latest_feedback"] = feedback
    st.session_state["session_finished"] = True
    st.session_state["session_started"] = False

    try:
        save_session(
            student_name=student,
            mode=st.session_state["current_mode"],
            topic=st.session_state["current_topic"],
            score=feedback.get("overall_score", 0),
            scores=feedback,
            feedback=json.dumps(feedback, ensure_ascii=False),
        )
    except Exception as exc:
        st.warning("Feedback is ready, but saving it to PostgreSQL failed.")
        st.caption(str(exc))


def render_feature_card(icon, title, description, destination, key):
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3>{safe_text(title)}</h3>
            <p>{safe_text(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        f"Open {title}  →",
        key=key,
        type="secondary",
        use_container_width=True,
    ):
        go(destination)


# =========================================================
# TOP BRAND HEADER
# =========================================================

header_left, header_right = st.columns([3, 2], gap="medium")

with header_left:
    st.markdown(
        """
        <div style="padding:10px 0 4px;">
            <div class="brand">Aurex</div>
            <div class="brand-caption">
                AI-powered GD & placement preparation
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        f"""
        <div class="welcome-text" style="padding:10px 0 4px;">
            Welcome back<br>
            <strong style="color:#242020;">{safe_text(student)}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="top-divider"></div>', unsafe_allow_html=True)


# =========================================================
# TOP NAVIGATION
# =========================================================

current_page = st.session_state["page"]

nav_items = [
    ("Home", "Dashboard"),
    ("GD Practice", "GD Practice"),
    ("AI Feedback", "AI Feedback"),
    ("Performance", "Performance"),
    ("Resume ATS", "Resume ATS Analyzer"),
    ("Log out", "LOGOUT"),
]

nav_cols = st.columns([1, 1.15, 1.05, 1.05, 1.15, 0.8], gap="small")

for col, (label, destination) in zip(nav_cols, nav_items):
    with col:
        if destination == "LOGOUT":
            if st.button(
                label,
                key="nav_logout",
                use_container_width=True,
                type="secondary",
            ):
                logout()
        else:
            if st.button(
                label,
                key=f"nav_{destination}",
                use_container_width=True,
                type="secondary",
            ):
                go(destination)

st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)


# =========================================================
# LOAD PRACTICE HISTORY
# =========================================================

try:
    sessions = get_sessions(student_name=student) or []
except Exception as exc:
    sessions = []
    st.error("Could not load PostgreSQL practice history.")

    with st.expander("Technical details"):
        st.code(str(exc))

score_list = []

for item in sessions:
    try:
        score_list.append(float(item.get("score", 0) or 0))
    except (TypeError, ValueError):
        score_list.append(0.0)

avg = round(sum(score_list) / len(score_list), 1) if score_list else 0
best = max(score_list) if score_list else 0

recent_scores = score_list[:5]
recent_avg = (
    round(sum(recent_scores) / len(recent_scores), 1)
    if recent_scores
    else 0
)


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state["page"] == "Dashboard":

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">YOUR PREPARATION WORKSPACE</div>
            <h1>Welcome back, {safe_text(student)}.</h1>
            <p>
                Build confidence, sharpen communication, and prepare for
                placements — one practice session at a time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-heading">Your overview</div>
        <p class="section-description">
            A snapshot of your group discussion practice and progress.
        </p>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4, gap="medium")

    dashboard_metrics = [
        ("GD Sessions", len(sessions), "Completed discussions"),
        ("Average Score", f"{avg}/100", "Across your sessions"),
        ("Personal Best", f"{best:.0f}/100", "Your highest score"),
        ("Recent Average", f"{recent_avg}/100", "Last five sessions"),
    ]

    for col, (label, value, note) in zip(cols, dashboard_metrics):
        with col:
            metric(label, value, note)

    st.markdown(
        """
        <div class="section-heading">Your preparation workspace</div>
        <p class="section-description">
            Choose a practice mode or review your progress.
        </p>
        """,
        unsafe_allow_html=True,
    )

    features = [
        (
            "💬",
            "Topic-Based GD",
            "Choose a topic and practise explaining your point of view.",
            "Topic-Based Practice",
        ),
        (
            "⚡",
            "Live GD Challenge",
            "Try a surprise topic and organise your thoughts under pressure.",
            "Live GD Challenge",
        ),
        (
            "🤖",
            "AI GD Sessions",
            "Practise with three AI participants sharing different viewpoints.",
            "AI GD Sessions",
        ),
        (
            "✦",
            "AI Feedback",
            "Review your scores, strengths, and areas to improve.",
            "AI Feedback",
        ),
    ]

    for start in range(0, len(features), 2):
        cols = st.columns(2, gap="medium")

        for col, feature in zip(cols, features[start:start + 2]):
            icon, title, description, destination = feature

            with col:
                render_feature_card(
                    icon,
                    title,
                    description,
                    destination,
                    key=f"dashboard_{destination}",
                )

    st.markdown(
        """
        <div class="section-heading">Career readiness</div>
        <p class="section-description">
            Keep your resume and placement preparation moving forward.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel">
            <div class="page-eyebrow">RESUME TOOL</div>
            <h3>Resume & ATS Analyzer</h3>
            <p class="small-muted">
                Review your resume and identify areas to improve
                before applying for internships and placements.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Analyze resume  →",
        key="dashboard_resume",
        type="secondary",
        use_container_width=True,
    ):
        go("Resume ATS Analyzer")

    st.markdown(
        """
        <div class="section-heading">Recent practice</div>
        <p class="section-description">
            Your latest completed discussions and scores.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if sessions:
        for item in sessions[:5]:
            topic = safe_text(item.get("topic", "GD Practice"))
            mode_name = safe_text(item.get("mode", "Practice"))
            created = safe_text(item.get("created_at", ""))
            score = safe_text(item.get("score", 0))

            st.markdown(
                f"""
                <div class="panel" style="padding:17px 20px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;
                                gap:14px; align-items:center; flex-wrap:wrap;">
                        <div style="min-width:0; flex:1;">
                            <div style="font-weight:750; overflow-wrap:anywhere;">
                                {topic}
                            </div>
                            <div class="small-muted">
                                {mode_name} · {created}
                            </div>
                        </div>
                        <div style="font-family:Manrope,sans-serif;
                                    font-weight:800; color:#242020;">
                            {score}/100
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button(
            "View all practice history  →",
            key="dashboard_all_history",
            type="secondary",
        ):
            go("Practice History")
    else:
        st.markdown(
            """
            <div class="panel">
                <h3>Your progress starts here</h3>
                <p class="small-muted">
                    Complete your first discussion to see your scores
                    and feedback here.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# GD PRACTICE HUB
# =========================================================

elif st.session_state["page"] == "GD Practice":

    st.markdown(
        '<div class="page-eyebrow">AUREX · GD PREPARATION</div>',
        unsafe_allow_html=True,
    )
    st.title("Explore your potential")

    st.markdown(
        """
        <p class="page-description">
            Choose the style of practice that suits your preparation.
            Build confidence one discussion at a time.
        </p>
        """,
        unsafe_allow_html=True,
    )

    hub_features = [
        (
            "💬",
            "Topic-Based Group Discussion",
            "Choose from practice topics or enter your own. Share your arguments and receive AI feedback.",
            "Explore topic-based practice",
            "Topic-Based Practice",
        ),
        (
            "⚡",
            "Live GD Challenge",
            "Get a surprise topic and practise structuring your thoughts under pressure.",
            "Start live challenge",
            "Live GD Challenge",
        ),
        (
            "🤖",
            "AI GD Sessions",
            "Practise with three AI participants offering practical, analytical, and critical viewpoints.",
            "Start AI GD session",
            "AI GD Sessions",
        ),
    ]

    for start in range(0, len(hub_features), 2):
        cols = st.columns(2, gap="medium")

        for col, feature in zip(cols, hub_features[start:start + 2]):
            icon, title, description, button_label, destination = feature

            with col:
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <div class="feature-icon">{icon}</div>
                        <h3>{safe_text(title)}</h3>
                        <p>{safe_text(description)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    f"{button_label}  →",
                    key=f"hub_{destination}",
                    type="secondary",
                    use_container_width=True,
                ):
                    go(destination)


# =========================================================
# DISCUSSION PAGES
# =========================================================

elif st.session_state["page"] in [
    "Topic-Based Practice",
    "Live GD Challenge",
    "AI GD Sessions",
]:

    page = st.session_state["page"]
    live = page == "Live GD Challenge"
    ai_sessions = page == "AI GD Sessions"

    if live:
        mode = "Live GD Challenge"
    elif ai_sessions:
        mode = "AI GD Sessions"
    else:
        mode = "Topic Practice"

    st.markdown(
        '<div class="page-eyebrow">PRACTICE WORKSPACE</div>',
        unsafe_allow_html=True,
    )
    st.title(page)

    st.markdown(
        """
        <p class="page-description">
            Express your ideas clearly, support your points with reasoning,
            and respond thoughtfully to other participants.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if ai_sessions:
        st.info(
            "Meet Arjun, Meera, and Rohan. They represent practical, "
            "analytical, and critical viewpoints. Their contributions "
            "are text-based in this version."
        )

    if (
        not st.session_state["session_started"]
        and not st.session_state["session_finished"]
    ):
        with st.container(border=True):
            difficulty = st.selectbox(
                "Difficulty",
                ["Beginner", "Intermediate", "Advanced"],
                index=2 if live else 1,
                key=f"difficulty_{mode}",
            )

            if live:
                st.info(
                    "A surprise topic will be generated for you. "
                    "The webcam preview is available during the discussion."
                )
                selected_topic = "Generate a surprise topic"
                custom = ""
            else:
                topics = ["Generate a topic with Gemini AI"] + TOPICS.get(
                    difficulty, []
                )

                selected_topic = st.selectbox(
                    "Choose a topic",
                    topics,
                    key=f"topic_choice_{mode}",
                )

                custom = st.text_input(
                    "Or enter your own topic (optional)",
                    placeholder="Should college attendance be compulsory?",
                    key=f"custom_topic_{mode}",
                )

            if st.button(
                "Generate topic & start" if live else "Start discussion",
                type="secondary",
                use_container_width=True,
                key=f"start_{mode}",
            ):
                try:
                    with st.spinner("Preparing your topic..."):
                        if not live and custom.strip():
                            topic = custom.strip()
                        elif (
                            live
                            or selected_topic == "Generate a topic with Gemini AI"
                        ):
                            topic = generate_topic(difficulty)
                        else:
                            topic = selected_topic

                    if not topic or not str(topic).strip():
                        st.error("Could not generate a topic. Please try again.")
                    else:
                        start_session(str(topic).strip(), difficulty, mode)
                        st.rerun()

                except Exception as exc:
                    st.error("Could not prepare the discussion topic.")
                    st.caption(str(exc))

    if (
        st.session_state["session_started"]
        and st.session_state["current_mode"] == mode
    ):
        st.markdown(
            f"""
            <div class="topic-box">
                <div class="page-eyebrow">DISCUSSION TOPIC</div>
                <h2>{safe_text(st.session_state["current_topic"])}</h2>
                <div class="small-muted">
                    Difficulty: {safe_text(st.session_state["current_difficulty"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_chat(mode)

        with st.form(f"response_form_{mode}", clear_on_submit=True):
            response = st.text_area(
                "Your contribution",
                placeholder=(
                    "Share your view, explain your reasoning, "
                    "and add an example..."
                ),
                height=130,
            )

            submitted = st.form_submit_button(
                "Submit response",
                type="secondary",
                use_container_width=True,
            )

        if submitted:
            if not response.strip():
                st.warning("Write a response before submitting.")
            else:
                st.session_state["discussion"].append(
                    {
                        "role": "user",
                        "content": response.strip(),
                    }
                )

                try:
                    # In the AI GD room, each participant gets a turn.
                    # Other modes retain one AI response per submission.
                    if ai_sessions:
                        with st.spinner("Your AI participants are discussing..."):
                            for participant in PARTICIPANTS:
                                reply = get_participant_reply(participant)

                                st.session_state["discussion"].append(
                                    {
                                        "role": "assistant",
                                        "speaker": participant["name"],
                                        "content": reply,
                                    }
                                )
                    else:
                        with st.spinner("The AI participant is responding..."):
                            reply = get_ai_response(
                                st.session_state["current_topic"],
                                st.session_state["discussion"],
                                st.session_state["current_difficulty"],
                            )

                        st.session_state["discussion"].append(
                            {
                                "role": "assistant",
                                "speaker": "Aurex AI Participant",
                                "content": str(reply),
                            }
                        )

                    st.rerun()

                except Exception as exc:
                    st.error("An AI participant could not respond.")
                    st.caption(str(exc))

        if st.button(
            "Finish & get feedback",
            key=f"finish_{mode}",
            type="secondary",
            use_container_width=True,
        ):
            finish_session()
            st.rerun()

    if (
        st.session_state["session_finished"]
        and st.session_state["current_mode"] == mode
    ):
        st.success("Discussion completed. Your feedback is ready.")
        render_feedback(st.session_state["latest_feedback"])

        if st.button(
            "Start another session",
            type="secondary",
            key=f"another_{mode}",
        ):
            st.session_state["session_finished"] = False
            st.session_state["session_started"] = False
            st.session_state["discussion"] = []
            st.session_state["latest_feedback"] = None
            st.session_state["current_topic"] = ""
            go(page)


# =========================================================
# AI FEEDBACK
# =========================================================

elif st.session_state["page"] == "AI Feedback":

    st.markdown(
        '<div class="page-eyebrow">YOUR RESULTS</div>',
        unsafe_allow_html=True,
    )
    st.title("AI Feedback")

    st.markdown(
        """
        <p class="page-description">
            Understand what you did well and what you can improve
            in your next group discussion.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state["latest_feedback"]:
        render_feedback(st.session_state["latest_feedback"])

    elif sessions:
        latest = sessions[0]
        st.markdown(f"### {safe_text(latest.get('topic', 'Latest discussion'))}")

        data = latest.get("scores", {})

        if not isinstance(data, dict) or not data:
            try:
                data = json.loads(latest.get("feedback", "{}"))
            except (TypeError, json.JSONDecodeError):
                data = {}

        render_feedback(data)

    else:
        st.markdown(
            """
            <div class="panel">
                <h3>Your first feedback report is waiting</h3>
                <p class="small-muted">
                    Complete a discussion to receive personalised feedback.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Start practising  →", type="secondary"):
            go("GD Practice")


# =========================================================
# PERFORMANCE ANALYTICS
# =========================================================

elif st.session_state["page"] == "Performance":

    st.markdown(
        '<div class="page-eyebrow">PROGRESS OVER TIME</div>',
        unsafe_allow_html=True,
    )
    st.title("Performance Analytics")

    st.markdown(
        """
        <p class="page-description">
            Track your discussion scores and review your recent practice.
        </p>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3, gap="medium")

    performance_metrics = [
        ("Completed sessions", len(sessions), "Total saved discussions"),
        ("Average score", f"{avg}/100", "Across all sessions"),
        ("Personal best", f"{best:.0f}/100", "Highest score"),
    ]

    for col, (label, value, note) in zip(cols, performance_metrics):
        with col:
            metric(label, value, note)

    if sessions:
        df = pd.DataFrame(sessions)

        if "score" in df.columns:
            df["score"] = pd.to_numeric(df["score"], errors="coerce")
            df = df.dropna(subset=["score"]).iloc[::-1].copy()
            df["Session"] = range(1, len(df) + 1)

            st.markdown(
                '<div class="section-heading">Score trend</div>',
                unsafe_allow_html=True,
            )
            st.line_chart(df.set_index("Session")["score"])

            st.markdown(
                '<div class="section-heading">Recent sessions</div>',
                unsafe_allow_html=True,
            )

            columns = [
                column
                for column in ["topic", "mode", "score", "created_at"]
                if column in df.columns
            ]

            st.dataframe(
                df[columns].iloc[::-1],
                use_container_width=True,
                hide_index=True,
            )

            if st.button("Open full practice history  →", type="secondary"):
                go("Practice History")
        else:
            st.info("Your saved sessions do not contain score data yet.")
    else:
        st.info("Complete a discussion to see your progress chart.")


# =========================================================
# PRACTICE HISTORY
# =========================================================

elif st.session_state["page"] == "Practice History":

    st.markdown(
        '<div class="page-eyebrow">PAST PRACTICE</div>',
        unsafe_allow_html=True,
    )
    st.title("Practice History")

    st.markdown(
        """
        <p class="page-description">
            Revisit your completed sessions and their feedback.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if not sessions:
        st.info("No completed sessions yet.")

        if st.button("Start topic practice", type="secondary"):
            go("Topic-Based Practice")
    else:
        df = pd.DataFrame(sessions)

        columns = [
            column
            for column in ["topic", "mode", "score", "created_at"]
            if column in df.columns
        ]

        st.dataframe(
            df[columns].rename(
                columns={
                    "topic": "Topic",
                    "mode": "Practice type",
                    "score": "Score",
                    "created_at": "Date",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        labels = {
            (
                f"{item.get('topic', 'Practice')} — "
                f"{item.get('created_at', '')} (ID {item.get('id')})"
            ): item
            for item in sessions
        }

        choice = st.selectbox("View session details", list(labels.keys()))
        item = labels[choice]

        st.markdown(f"**Topic:** {safe_text(item.get('topic', ''))}")
        st.markdown(f"**Practice type:** {safe_text(item.get('mode', ''))}")
        st.markdown(f"**Score:** {safe_text(item.get('score', 0))}/100")

        data = item.get("scores", {})

        if not isinstance(data, dict) or not data:
            try:
                data = json.loads(item.get("feedback", "{}"))
            except (TypeError, json.JSONDecodeError):
                data = {}

        if data:
            render_feedback(data)


# =========================================================
# RESUME ATS ANALYZER
# =========================================================

elif st.session_state["page"] == "Resume ATS Analyzer":

    st.markdown(
        '<div class="page-eyebrow">CAREER TOOLS</div>',
        unsafe_allow_html=True,
    )
    st.title("Resume ATS Analyzer")

    st.markdown(
        """
        <p class="page-description">
            Review your resume and identify opportunities to improve
            your placement applications.
        </p>
        """,
        unsafe_allow_html=True,
    )

    show_resume_analyzer()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="app-footer">
        <strong style="color:#242020;">Aurex</strong>
        &nbsp;·&nbsp; AI-powered GD & placement preparation
        <br>
        Practise consistently. Improve one skill at a time.
    </div>
    """,
    unsafe_allow_html=True,
)
