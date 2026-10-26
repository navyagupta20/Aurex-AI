
import json
import os
import random
import re

from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

TOPICS = {
    "Beginner": [
        "Should college attendance be compulsory?",
        "Is online learning better than classroom learning?",
        "Should students participate in extracurricular activities?",
        "Are smartphones helpful for students?",
        "Should exams be replaced with continuous assessment?",
        "Is teamwork more important than individual talent?",
        "Should every student learn basic programming?",
        "Does social media do more harm than good?",
    ],
    "Intermediate": [
        "Will artificial intelligence create more jobs than it replaces?",
        "Should work-from-home become a permanent option?",
        "Is a college degree necessary for career success?",
        "Should companies prioritise skills over academic marks?",
        "Can technology solve most environmental problems?",
        "Should internships be compulsory for university students?",
        "Is data privacy more important than convenience?",
        "Should four-day workweeks become the norm?",
    ],
    "Advanced": [
        "Should governments regulate generative artificial intelligence?",
        "Can economic growth and environmental sustainability coexist?",
        "Should AI-generated content require mandatory disclosure?",
        "Is universal basic income a practical response to automation?",
        "Should personal data be treated as a form of property?",
        "Can social media platforms be neutral public spaces?",
        "Should companies be legally responsible for algorithmic bias?",
        "Does technological progress always improve society?",
    ],
}


def get_client():
    if not API_KEY or API_KEY in {
        "YOUR_GEMINI_API_KEY",
        "your_gemini_api_key_here",
    }:
        raise ValueError(
            "Gemini API key is missing. Add your valid key to .env."
        )

    return genai.Client(api_key=API_KEY)


def ask_gemini(prompt):
    client = get_client()

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        answer = getattr(response, "text", None)

        if not answer or not answer.strip():
            raise RuntimeError(
                "Gemini returned an empty response. Please try again."
            )

        return answer.strip()

    except Exception as exc:
        raise RuntimeError(
            f"Gemini request failed using {MODEL_NAME}: {exc}"
        ) from exc

    finally:
        client.close()


def generate_topic(difficulty="Intermediate"):
    difficulty = difficulty if difficulty in TOPICS else "Intermediate"

    try:
        topic = ask_gemini(
            f"Generate one clear, debatable group discussion question "
            f"for a college student. Difficulty: {difficulty}. "
            "Keep it suitable for placement preparation. "
            "Return only the question, without numbering or explanation."
        ).strip().strip('"').strip("'")

        if topic:
            return topic

    except Exception:
        pass

    return random.choice(TOPICS[difficulty])


def get_ai_response(topic, conversation, difficulty="Intermediate"):
    transcript = "\n".join(
        f"{'Student' if item.get('role') == 'user' else 'AI participant'}: "
        f"{item.get('content', '')}"
        for item in conversation[-12:]
    )

    prompt = f"""
You are an AI student participating in a realistic group discussion.

Topic: {topic}
Difficulty: {difficulty}

Conversation so far:
{transcript}

Respond as another participant with one clear argument, reasoning,
or example. You may respectfully disagree or add another perspective.
Keep your response between 60 and 110 words.

Do not score or evaluate the student.
Return only your contribution.
"""

    return ask_gemini(prompt)


def _extract_json(text):
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        text.strip(),
        flags=re.IGNORECASE,
    )

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)

    if match:
        data = json.loads(match.group(0))
        if isinstance(data, dict):
            return data

    raise ValueError("Gemini did not return valid JSON feedback.")


def _normalise_feedback(data):
    fields = [
        "relevance",
        "clarity",
        "reasoning",
        "examples",
        "engagement",
    ]

    result = {}

    for field in fields:
        try:
            result[field] = max(
                0,
                min(100, round(float(data.get(field, 0)))),
            )
        except (ValueError, TypeError):
            result[field] = 0

    try:
        result["overall_score"] = max(
            0,
            min(100, round(float(data.get("overall_score")))),
        )
    except (ValueError, TypeError):
        result["overall_score"] = round(
            sum(result[field] for field in fields) / len(fields)
        )

    for field in ["strengths", "improvements"]:
        value = data.get(field, [])

        if isinstance(value, str):
            value = [value]

        result[field] = (
            [str(item) for item in value[:5]]
            if isinstance(value, list)
            else []
        )

    result["feedback"] = str(
        data.get(
            "feedback",
            "Keep practising clear arguments and relevant examples.",
        )
    )

    result["next_step"] = str(
        data.get(
            "next_step",
            "Practise another topic and support each point with reasoning.",
        )
    )

    return result


def evaluate_discussion(topic, conversation):
    student_messages = [
        message.get("content", "").strip()
        for message in conversation
        if message.get("role") == "user"
        and message.get("content", "").strip()
    ]

    if not student_messages:
        raise ValueError(
            "Make at least one contribution before requesting feedback."
        )

    transcript = "\n".join(
        f"{'Student' if item.get('role') == 'user' else 'AI participant'}: "
        f"{item.get('content', '')}"
        for item in conversation
    )

    prompt = f"""
Act as a constructive group discussion coach for university students
preparing for placements. Evaluate ONLY the student's contributions.

Topic: {topic}

Transcript:
{transcript}

Score each category from 0 to 100:
- relevance: How directly the points address the topic.
- clarity: How clearly the ideas are expressed.
- reasoning: Quality of explanations and logical support.
- examples: Use of relevant examples or practical situations.
- engagement: Responsiveness to the discussion.

Give an overall_score from 0 to 100.
Be fair to beginners and do not reward length alone.
Base all feedback on the transcript.

Return ONLY valid JSON in this structure:
{{
  "relevance": 0,
  "clarity": 0,
  "reasoning": 0,
  "examples": 0,
  "engagement": 0,
  "overall_score": 0,
  "strengths": ["specific strength"],
  "improvements": ["specific improvement"],
  "feedback": "constructive feedback",
  "next_step": "one practical exercise"
}}

Use integer scores and provide actionable feedback.
Return no Markdown fences or extra text.
"""

    response = ask_gemini(prompt)
    feedback = _extract_json(response)

    return _normalise_feedback(feedback)
