# Aurex - AI-Powered GD & Placement Preparation Platform

Aurex is an AI-powered web application designed to help students prepare for campus placements through group discussion practice, AI-generated feedback, resume analysis, and performance tracking.

## ✨ Features

- **AI-Powered GD Practice:** Practise group discussions with AI-generated topics and text-based AI responses.
- **Topic Generation:** Explore discussion topics for placement preparation.
- **AI Feedback & Evaluation:** Receive structured feedback on relevance, clarity, reasoning, strengths, and areas for improvement.
- **Resume ATS Analyzer:** Upload a PDF resume for analysis and identify potential areas for improvement.
- **User Authentication:** Register and log in with password hashing.
- **Performance Tracking:** Review discussion scores and monitor practice progress.
- **Practice History:** Save and revisit previous discussion sessions and feedback.
- **Interactive Dashboard:** Access practice features, resume analysis, and performance information through a Streamlit interface.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language and application logic |
| Streamlit | Frontend and interactive user interface |
| Google Gemini API | Topic generation, AI discussion responses, and feedback |
| PostgreSQL | Database configured for persistent data storage |
| SQLAlchemy | Database models, queries, and session management |
| Pandas | Organizing and processing performance data |
| bcrypt | Password hashing and verification |
| PyPDF | Reading PDF resumes |
| python-dotenv | Loading environment variables |

## 🏗️ Application Architecture

- **Frontend:** Streamlit provides the dashboard, forms, navigation, and interactive practice screens.
- **Application Logic:** Python modules handle authentication, AI interactions, resume analysis, and discussion evaluation.
- **AI Integration:** The Google Gemini API generates discussion topics, responses, and feedback.
- **Database Layer:** SQLAlchemy manages database operations for users and practice sessions, using the configured database URL.
- **Data Processing:** Pandas organizes performance data for display and tracking.

## 📁 Project Structure

```text
Aurex/
├── app.py
├── ai_coach.py
├── auth.py
├── auth_ui.py
├── database.py
├── resume_analyzer.py
├── requirements.txt
├── .env
└── pages/
    ├── 1_Topic_Practice.py
    ├── 2_Live_GD_Challenge.py
    ├── 3_Performance.py
    └── 4_Practice_History.py
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or later
- PostgreSQL database
- Google Gemini API key

### 1. Clone the repository

```powershell
git clone https://github.com/navyagupta20/Aurex-AI.git
cd Aurex-AI
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_url
```

Replace the example values with your own credentials. Never commit your `.env` file or expose API keys, database passwords, or other secrets.

Ensure that the environment variable names match those read by your application.

### 5. Run the application

```powershell
streamlit run app.py
```

Streamlit will display a local URL in your terminal. Open it in your browser to use Aurex.

## 🔐 Security Notes

- Passwords are hashed using bcrypt rather than stored as plain text.
- API keys and database credentials should be stored in environment variables.
- Keep `.env` and other files containing secrets out of version control.

---

*Built to help students practise smarter and prepare confidently for campus placements.*
