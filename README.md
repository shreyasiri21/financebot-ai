# FinanceBot — AI Personal Finance Chatbot

A conversational chatbot that answers personal finance questions using
Claude (Anthropic API) grounded in a structured Indian personal-finance
knowledge base. Built with Flask + vanilla HTML/CSS/JS ("passbook ledger"
themed chat UI).

## Features
- NLP-driven contextual Q&A on budgeting, tax regimes, investment
  instruments (PPF/ELSS/NPS/SIP/SGB/FD), credit scores, and emergency funds.
- LLM-based response generation (Claude) layered on a structured knowledge
  base for domain-specific, grounded answers.
- Clean chat interface with quick-start question chips, typing indicator,
  and session reset.

## 1. Local setup

```bash
cd financebot
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-ant-..."   # Windows: setx ANTHROPIC_API_KEY "sk-ant-..."
python app.py
```

Visit `http://localhost:5000`.

## 2. Project structure

```
financebot/
├── app.py                 # Flask backend + Claude API integration
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## 3. Deploy to GitHub + Render (free tier)

1. **Push to GitHub**
   ```bash
   cd financebot
   git init
   git add .
   git commit -m "FinanceBot: AI personal finance chatbot"
   git branch -M main
   git remote add origin https://github.com/<your-username>/financebot.git
   git push -u origin main
   ```
   Make sure `.env` files or real API keys are never committed.

2. **Create the Render web service**
   - Go to [render.com](https://render.com) → New → Web Service.
   - Connect your GitHub repo.
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
   - **Environment variable:** `ANTHROPIC_API_KEY` = your key (Render → Environment tab).
   - Deploy. Render will give you a live URL like `financebot.onrender.com`.

3. **Resume-ready link:** once live, add the Render URL to your resume/portfolio
   alongside this repo link.

## 4. Notes for extending this project

- Swap the in-memory `conversations` dict for Redis or a database if you
  need persistence across restarts / multiple server instances.
- Add authentication (e.g., Flask-Login) if you want per-user history.
- Expand `FINANCE_KNOWLEDGE_BASE` in `app.py` with more instruments, tax
  slabs, or region-specific rules as needed — the system prompt injects it
  directly into every conversation.
