
import streamlit as st
from pypdf import PdfReader
from io import BytesIO
from google import genai
import os
import json


def extract_resume_text(pdf_file):
    """Extract readable text from an uploaded PDF resume."""
    reader = PdfReader(BytesIO(pdf_file.getvalue()))

    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()


def analyze_resume(resume_text, job_description):
    """Use Gemini to compare a resume with a job description."""

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found. Please check your .env file."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a practical resume reviewer.

Compare the resume with the job description.

Return ONLY valid JSON in this format:
{{
    "match_score": 75,
    "summary": "Short overall assessment",
    "matching_skills": ["Python", "SQL"],
    "missing_skills": ["Docker", "AWS"],
    "strengths": ["Relevant project experience"],
    "improvements": ["Add measurable project results"]
}}

Rules:
- match_score must be an integer from 0 to 100.
- Base the assessment only on the information provided.
- Do not invent qualifications or experience.
- Missing skills should be skills requested by the job but not clearly shown in the resume.
- Keep the feedback constructive and suitable for a fresher.
- Return JSON only.

RESUME:
{resume_text[:15000]}

JOB DESCRIPTION:
{job_description[:10000]}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    result_text = response.text or ""
    result_text = result_text.strip()

    if result_text.startswith("```"):
        result_text = result_text.split("\n", 1)[-1]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        if result_text.lower().startswith("json"):
            result_text = result_text[4:].strip()

    result = json.loads(result_text)

    result["match_score"] = max(
        0, min(100, int(result.get("match_score", 0)))
    )

    for key in [
        "matching_skills",
        "missing_skills",
        "strengths",
        "improvements",
    ]:
        if not isinstance(result.get(key), list):
            result[key] = []

    result.setdefault("summary", "Analysis completed.")

    return result


def show_resume_analyzer():
    
    st.info(
        "Upload a text-based PDF resume. Scanned image-only PDFs "
        "may not provide readable text."
    )

    resume_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        key="resume_pdf",
    )

    job_description = st.text_area(
        "Paste the job description",
        placeholder="Paste the job responsibilities and required skills here...",
        height=220,
        key="resume_job_description",
    )

    if st.button(
        "Analyze My Resume",
        type="primary",
        use_container_width=True,
    ):
        if resume_file is None:
            st.warning("Please upload your resume PDF first.")
            return

        if not job_description.strip():
            st.warning("Please paste the job description first.")
            return

        try:
            with st.spinner("Reading your resume and analyzing the job match..."):
                resume_text = extract_resume_text(resume_file)

                if len(resume_text) < 50:
                    st.error(
                        "I couldn't extract enough text from this PDF. "
                        "Please upload a text-based PDF resume."
                    )
                    return

                result = analyze_resume(
                    resume_text,
                    job_description.strip(),
                )

            st.session_state["resume_analysis"] = result

        except json.JSONDecodeError:
            st.error(
                "The AI response could not be read. Please try again."
            )
            return
        except Exception as error:
            st.error(f"Analysis failed: {error}")
            return

    result = st.session_state.get("resume_analysis")

    if result:
        st.divider()
        st.subheader("Your Resume Analysis")

        score = result["match_score"]
        st.metric("Resume Match Score", f"{score}%")
        st.progress(score / 100)

        st.write("**Overall assessment**")
        st.write(result["summary"])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Matching Skills")
            if result["matching_skills"]:
                for skill in result["matching_skills"]:
                    st.write(f"✅ {skill}")
            else:
                st.write("No clear matching skills identified.")

        with col2:
            st.markdown("#### Skills to Improve")
            if result["missing_skills"]:
                for skill in result["missing_skills"]:
                    st.write(f"• {skill}")
            else:
                st.write("No major missing skills identified.")

        st.markdown("#### Your Strengths")
        for item in result["strengths"]:
            st.write(f"✓ {item}")

        st.markdown("#### Suggested Improvements")
        for item in result["improvements"]:
            st.write(f"→ {item}")

        st.caption(
            "The match score is an AI-generated estimate, not a guarantee "
            "of passing an employer's ATS."
        )
