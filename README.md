# FoundrAI – AI Startup Co-Founder Platform

FoundrAI is a production-quality, multi-agent dashboard designed to help entrepreneurs validate startup ideas, perform market research, analyze competitors, structure business models, forecast financials, and generate investor-ready documents. 

Built using Python, Streamlit, SQLite, and Google Gemini, it provides a high-fidelity co-founder experience. It features a local user database, 12 independent AI agents collaborating inside a virtual board room, responsive charts, and professional PDF generation.

---

## Key Features

1. **Secure Local Authentication**: SQLite database with user registration, login, logout, and password hashing using PBKDF2 (SHA-256).
2. **Remember Me Login persistence**: Persists sessions across page reloads using a secure local token.
3. **12-Agent Board of Co-Founders**:
   - **Startup Idea Validator**: Computes feasibility and validation alignment.
   - **Market Research Agent**: Calculates market sizes (TAM, SAM, SOM).
   - **Competitor Analysis Agent**: Evaluates competitor strengths, weaknesses, and unaddressed gaps.
   - **SWOT Analysis Agent**: Structures a Strengths, Weaknesses, Opportunities, and Threats canvas.
   - **Business Model Generator**: Maps out the Business Model Canvas parameters.
   - **Revenue Strategy Agent**: Tailors subscription tiers, ACVs, and channels.
   - **MVP Planner**: Structures a 12-week development roadmap and tech stack.
   - **Go-To-Market Strategy Agent**: Creates launch campaigns and action checklists.
   - **Financial Forecast Agent**: Projects 3-year revenues, expenses, and profits.
   - **Funding Strategy Agent**: Formulates seed target allocations and SAFE valuations.
   - **Risk Assessment Agent**: Formulates risk mitigation plans.
   - **Investor Pitch Generator**: Formulates a 10-slide deck outline and elevator pitch.
4. **Dual Engine Mode**:
   - **Demo Mode (Default)**: Runs completely offline without any API keys. Leverages pre-configured intelligent advice templates across SaaS, FinTech, E-commerce, HealthTech, AI/DeepTech, and CleanEnergy industries.
   - **Gemini Mode (Optional)**: Automatically triggers live Gemini model queries when a valid `GEMINI_API_KEY` is supplied in the `.env` file.
5. **Interactive Financial Graphs**: Renders grouped bar charts of financial forecasts using Plotly.
6. **Report Export**: Compiles report pages and dynamic tables into a styled PDF document using ReportLab.
7. **Premium Dark UI Theme**: High-fidelity dark slate and emerald styling, customized cards, and real-time agent execution status trackers.

---

## Project Structure

```
FoundrAI/
├── .streamlit/
│   └── config.toml         # Theme settings and page constraints
├── assets/
│   └── images/
│       └── logo.png        # Brand logo asset (generated dynamically)
├── database.py             # SQLite setup, password hashing, and user query functions
├── auth.py                 # Sign-in/signup routes and login persistence token
├── ai_service.py           # Gemini API initializer, validator, and fallback handler
├── agents.py               # 12 specialized co-founder agents and orchestrator logic
├── utils.py                # Markdown to PDF document compiler
├── styles.css              # Custom CSS stylesheet (glassmorphism cards, layouts)
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
├── README.md               # User documentation
└── app.py                  # Main Streamlit router and dashboard views
```

---

## Getting Started

### Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 1. Install Dependencies
Navigate to the project root and run:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Gemini Mode)
To use live AI models, create a `.env` file from the example:
```bash
cp .env.example .env
```
Open `.env` and configure your API key:
```ini
GEMINI_API_KEY=AIzaSy...your_gemini_key...
```

If this file does not exist, or the key is invalid, the platform will automatically run in **Demo Mode** offline without crashes.

### 3. Run the Application
Start the Streamlit development server:
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Deployment Instructions

### Deploying to Streamlit Community Cloud
1. Push this repository to a public/private GitHub repository.
2. Visit [Streamlit Share](https://share.streamlit.io/) and log in with GitHub.
3. Click **New App** and select your repository, branch, and `app.py` as the entrypoint path.
4. (Optional) To enable Gemini Mode on the cloud, expand **Advanced settings**, and in **Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key"
   ```
5. Click **Deploy**. Streamlit Cloud will automatically build dependencies from `requirements.txt` and launch the platform.
