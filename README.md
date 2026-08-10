# AI Job Transition Safety Assistant

## Problem Statement
Employees may resign from their current job before their new employment is fully confirmed. If the new employer withdraws the offer, delays joining, or fails background verification, the employee may be left without a job.

## Solution
This application helps employees safely transition from their current job to a new job by analyzing job offers, resignation timing, background verification status, joining conditions, notice periods, and employment documents using AI.

## Features
- **Job Transition Assessment:** Evaluate your current risk with a comprehensive form.
- **AI Risk Analysis:** Get personalized insights on positive factors, risk factors, and actionable next steps.
- **Safety Score Engine:** A transparent, rule-based risk engine that grades your transition safety (0-100).
- **Offer Letter Analyzer:** Upload your offer letter (PDF, DOCX, TXT) and let AI extract key clauses, missing information, and generate relevant HR questions.
- **Notice Period Calculator:** Determine your expected last working day and employment gap to avoid overlap.
- **History:** Keep track of your past assessments and document analyses safely locally using SQLite.

## Technology Stack
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS (Bootstrap), Jinja2
- **Database:** SQLite
- **AI Integration:** Google Gemini API
- **Document Processing:** PyPDF2, python-docx

## Project Architecture
```text
ai-job-transition-safety/
│
├── app.py                  # Main Flask application and routing
├── ai_service.py           # Gemini API integration and prompting
├── database.py             # SQLite setup and queries
├── document_analyzer.py    # Text extraction for PDF, DOCX, TXT
├── risk_engine.py          # Rule-based score calculation
├── utils.py                # Date calculations
├── requirements.txt        # Dependencies
├── .env.example            # Environment variables template
├── README.md               # Documentation
├── static/
│   └── css/
│       └── style.css       # Custom styles
├── templates/              # HTML templates (base, dashboard, assessment, etc.)
├── uploads/                # Temporary document storage
└── data/                   # SQLite database directory (app.db)
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd ai-job-transition-safety
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   - Rename `.env.example` to `.env`
   - Add your Gemini API Key to `GEMINI_API_KEY`.
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Running Locally

1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to `http://127.0.0.1:5000/`.

## Demo Instructions

For hackathon presentations, use the **"Load Demo Data"** button located in the sidebar. This will pre-populate a risky job transition scenario. Simply click the button, review the populated form on the Assessment page, and click **"Analyze Transition Risk"** to showcase the application's capabilities.

## Disclaimer
*This application provides AI-assisted informational guidance based on the information provided by the user. It does not provide legal, financial, employment, or professional advice. Users should verify important employment decisions with the employer or a qualified professional.*
