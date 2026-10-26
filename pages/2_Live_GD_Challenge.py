
import json
import os
import time

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from google import genai
from google.genai import types

from ai_coach import TOPICS, generate_topic, get_ai_response, evaluate_discussion
from database import save_session

load_dotenv(override=True)

st.set_page_config(
    page_title="Live GD Challenge | Aurex",
    page_icon="🎙️",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}
.title {
    font-size: 34px;
    font-weight: 800;
    color: #171717;
}
.subtitle {
    color: #77716D;
    margin-bottom: 22px;
}
.mic-panel {
    padding: 20px;
    border: 1px solid #E2DAD7;
    border-radius: 14px;
    background: #FFF9F8;
    margin: 12px 0;
}
div.stButton > button[kind="primary"] {
    background: #8F2945;
    color: white;
    border: none;
    border-radius: 9px;
    min-height: 42px;
}
</style>
""", unsafe_allow_html=True)


def transcribe_audio(audio_file):
    """Transcribe the user's recorded contribution with Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from your .env file.")

    client = genai.Client(api_key=api_key)

    try:
        audio_part = types.Part.from_bytes(
            data=audio_file.getvalue(),
            mime_type=audio_file.type or "audio/wav",
        )

        response = client.models.generate_content(
            model=model,
            contents=[
                "Transcribe the spoken words in this audio accurately. "
                "Return only the spoken words. Do not answer, summarize, "
                "or add explanations. If no speech is audible, return "
                "an empty response.",
                audio_part,
            ],
        )

        transcript = (response.text or "").strip()

        if not transcript:
            raise ValueError(
                "No speech was detected. Please record your contribution again."
            )

        return transcript

    finally:
        client.close()


def speak_text(text):
    """Display browser-based speech playback controls."""
    safe_text = json.dumps(text)

    html = f"""
    <div style="font-family:Arial,sans-serif;padding:8px 0;">
      <button id="speakButton"
        style="background:#8F2945;color:white;border:0;border-radius:8px;
        padding:11px 16px;cursor:pointer;font-size:14px;">
        🔊 Play AI response
      </button>
      <button id="stopButton"
        style="background:#f3f0ef;color:#333;border:0;border-radius:8px;
        padding:11px 16px;cursor:pointer;font-size:14px;margin-left:8px;">
        Stop
      </button>
      <span id="status"
        style="margin-left:8px;color:#777;font-size:12px;"></span>
    </div>
    <script>
      const textToSpeak = {safe_text};
      const status = document.getElementById("status");

      document.getElementById("speakButton").onclick = () => {{
        if (!("speechSynthesis" in window)) {{
          status.textContent = "Speech playback is not supported.";
          return;
        }}

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = "en-IN";
        utterance.rate = 1;
        utterance.onstart = () => status.textContent = "Playing...";
        utterance.onend = () => status.textContent = "Finished";
        utterance.onerror = () => status.textContent = "Playback failed.";

        window.speechSynthesis.speak(utterance);
      }};

      document.getElementById("stopButton").onclick = () => {{
        if ("speechSynthesis" in window) {{
          window.speechSynthesis.cancel();
        }}
        status.textContent = "Stopped";
      }};
    </script>
    """

    components.html(html, height=65)


# Authentication
if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access Live GD Challenge.")
    st.stop()

user = st.session_state.get("user", {})
student_name = user.get("full_name", "Student")


# Page heading
st.markdown(
    '<div class="title">Live GD Challenge</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Speak naturally, practise with an AI '
    'participant, and improve your placement communication.</div>',
    unsafe_allow_html=True,
)


# Initialise session state
defaults = {
    "live_gd_messages": [],
    "live_gd_active": False,
    "live_gd_topic": "",
    "live_gd_started": None,
    "live_gd_feedback": None,
    "live_gd_saved": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Setup screen
if not st.session_state["live_gd_active"]:

    with st.container(border=True):
        st.subheader("Prepare for your discussion")

        difficulty = st.selectbox(
            "Difficulty",
            ["Beginner", "Intermediate", "Advanced"],
        )

        topic = st.selectbox(
            "Choose a topic",
            TOPICS[difficulty],
        )

        if st.button("Generate another topic"):
            try:
                st.session_state["live_gd_generated_topic"] = (
                    generate_topic(difficulty)
                )
                st.rerun()
            except Exception as error:
                st.error(f"Could not generate a topic: {error}")

        topic = st.session_state.get("live_gd_generated_topic", topic)
        st.info(topic)

        st.caption(
            "Your contributions will be recorded through the microphone. "
            "You do not need to type your arguments."
        )

        if st.button("Start live discussion", type="primary"):
            st.session_state["live_gd_active"] = True
            st.session_state["live_gd_topic"] = topic
            st.session_state["live_gd_difficulty"] = difficulty
            st.session_state["live_gd_messages"] = []
            st.session_state["live_gd_started"] = time.time()
            st.session_state["live_gd_feedback"] = None
            st.session_state["live_gd_saved"] = False
            st.session_state.pop("live_gd_generated_topic", None)
            st.session_state.pop("live_gd_last_reply", None)
            st.rerun()


# Active discussion
else:
    topic = st.session_state["live_gd_topic"]
    started = st.session_state["live_gd_started"]

    elapsed = int(time.time() - started)
    remaining = max(0, 15 * 60 - elapsed)

    st.subheader("Discussion topic")
    st.info(topic)

    st.metric(
        "Time remaining",
        f"{remaining // 60:02d}:{remaining % 60:02d}",
    )

    if remaining == 0:
        st.warning(
            "Your 15-minute discussion has ended. "
            "You can now request your feedback."
        )

    # Camera option
    with st.container(border=True):
        st.markdown("### 📷 Camera")

        camera_enabled = st.checkbox(
            "Turn camera on",
            key="live_gd_camera_enabled",
        )

        if camera_enabled:
            st.caption(
                "Allow camera permission if your browser asks. "
                "This feature takes a snapshot, not continuous video."
            )

            camera_image = st.camera_input(
                "Camera preview",
                key="live_gd_camera",
            )

            if camera_image is not None:
                st.image(
                    camera_image,
                    caption="Camera snapshot",
                    width=320,
                )
        else:
            st.caption("Camera is off.")

    # Discussion transcript
    st.markdown("### 💬 Discussion room")

    for index, message in enumerate(
        st.session_state["live_gd_messages"]
    ):
        is_student = message["role"] == "user"

        with st.chat_message("user" if is_student else "assistant"):
            st.markdown(
                "**Your contribution**"
                if is_student
                else "**AI participant**"
            )
            st.write(message["content"])

            if not is_student:
                if st.button(
                    "🔊 Play this response",
                    key=f"play_ai_{index}",
                ):
                    speak_text(message["content"])

    # Microphone section
    if remaining > 0 and not st.session_state["live_gd_feedback"]:

        with st.container(border=True):
            st.markdown("### 🎙️ Speak in your discussion")

            st.write(
                "Use the recording control below. Speak your argument, "
                "then stop the recording when you finish."
            )

            st.info(
                "MICROPHONE CONTROL: Look for the recording button below. "
                "If it is missing, the browser may not be rendering "
                "the audio input control."
            )

            recording = st.audio_input(
                "🎙️ Record your contribution",
                key="live_gd_audio",
            )

            if recording is None:
                st.caption(
                    "No recording submitted yet. Click the microphone "
                    "control to start recording."
                )

            if recording is not None:
                st.success("Recording received.")
                st.audio(recording)

                if st.button(
                    "Transcribe speech and get AI response",
                    type="primary",
                    key="transcribe_respond",
                ):
                    try:
                        with st.spinner("Transcribing your speech..."):
                            transcript = transcribe_audio(recording)

                        st.session_state["live_gd_messages"].append(
                            {
                                "role": "user",
                                "content": transcript,
                            }
                        )

                        with st.spinner("AI participant is responding..."):
                            reply = get_ai_response(
                                topic,
                                st.session_state["live_gd_messages"],
                                st.session_state.get(
                                    "live_gd_difficulty",
                                    "Intermediate",
                                ),
                            )

                        st.session_state["live_gd_messages"].append(
                            {
                                "role": "assistant",
                                "content": reply,
                            }
                        )

                        st.session_state["live_gd_last_reply"] = reply
                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"Audio processing failed: {error}"
                        )

            last_reply = st.session_state.get("live_gd_last_reply")

            if last_reply:
                st.markdown("### AI participant's latest response")
                st.write(last_reply)
                speak_text(last_reply)

    st.divider()

    # Discussion controls
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "End discussion and get feedback",
            type="primary",
        ):
            if not any(
                message["role"] == "user"
                for message in st.session_state["live_gd_messages"]
            ):
                st.warning("Record at least one contribution first.")
            else:
                try:
                    with st.spinner("Evaluating your discussion..."):
                        st.session_state["live_gd_feedback"] = (
                            evaluate_discussion(
                                topic,
                                st.session_state["live_gd_messages"],
                            )
                        )
                    st.rerun()

                except Exception as error:
                    st.error(f"Feedback failed: {error}")

    with col2:
        if st.button("Start a new discussion"):
            keys_to_clear = [
                "live_gd_active",
                "live_gd_messages",
                "live_gd_topic",
                "live_gd_started",
                "live_gd_feedback",
                "live_gd_difficulty",
                "live_gd_saved",
                "live_gd_last_reply",
                "live_gd_audio",
                "live_gd_camera",
                "live_gd_camera_enabled",
                "live_gd_generated_topic",
            ]

            for key in keys_to_clear:
                st.session_state.pop(key, None)

            st.rerun()

    # Feedback report
    feedback = st.session_state.get("live_gd_feedback")

    if feedback:
        st.divider()
        st.markdown("### 📊 Your performance report")

        st.metric(
            "Overall score",
            f'{feedback["overall_score"]}/100',
        )

        cols = st.columns(3)

        for index, field in enumerate(
            [
                "relevance",
                "clarity",
                "reasoning",
                "examples",
                "engagement",
            ]
        ):
            cols[index % 3].metric(
                field.title(),
                f'{feedback[field]}/100',
            )

        st.markdown("#### Strengths")

        for item in feedback["strengths"]:
            st.write(f"✓ {item}")

        st.markdown("#### Areas to improve")

        for item in feedback["improvements"]:
            st.write(f"• {item}")

        st.write(feedback["feedback"])
        st.info(feedback["next_step"])

        if not st.session_state["live_gd_saved"]:
            if st.button("Save discussion results", type="primary"):
                try:
                    save_session(
                        student_name=student_name,
                        mode="Live GD Challenge",
                        topic=topic,
                        score=feedback["overall_score"],
                        scores=json.dumps(feedback),
                        feedback=feedback["feedback"],
                    )

                    st.session_state["live_gd_saved"] = True
                    st.success("Discussion results saved.")

                except Exception as error:
                    st.error(
                        f"Could not save results: {error}"
                    )
        else:
            st.success("Discussion results have been saved.")
