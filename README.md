# FinanceBot — AI Personal Finance Chatbot

FinanceBot is an AI-powered conversational chatbot that provides educational guidance on Indian personal finance topics such as budgeting, taxation, investments, credit scores, and savings. It combines a Large Language Model (LLM) with a structured financial knowledge base to deliver contextual and domain-specific responses.

## Features

- AI-powered conversational chatbot using the Groq API and Llama model.
- Domain-specific financial assistance for:
  - Budgeting
  - Tax regimes
  - SIP, PPF, ELSS, NPS, FD and SGB
  - Credit scores (CIBIL)
  - Emergency funds
- Structured Indian personal-finance knowledge base for grounded responses.
- User-friendly chat interface with:
  - Typing indicator
  - Session reset
  - Passbook-style ledger UI
- Secure API key management using environment variables.

---

## Technologies Used

- Python
- Flask
- Groq API
- Llama 3.1 Model
- HTML
- CSS
- JavaScript
- Render
- GitHub

---

## Local Setup

### Clone the repository

```bash
git clone https://github.com/<your-username>/financebot.git
cd financebot
```

### Create a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure the API Key

Create an environment variable:

Windows

```bash
setx GROQ_API_KEY "your_groq_api_key"
```

Linux/macOS

```bash
export GROQ_API_KEY="your_groq_api_key"
```

### Run the application

```bash
python app.py
```

Open:

```
http://localhost:5000
```

---

## Project Structure

```
financebot/
│
├── app.py                 # Flask backend
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── README.md
```

---

## Deployment (Render)

### Push the project to GitHub

```bash
git init
git add .
git commit -m "FinanceBot"
git branch -M main
git remote add origin https://github.com/<your-username>/financebot.git
git push -u origin main
```

### Deploy on Render

1. Create a new **Web Service**.
2. Connect your GitHub repository.
3. Build Command:

```bash
pip install -r requirements.txt
```

4. Start Command

```bash
gunicorn app:app
```

5. Add the following environment variable:

```
GROQ_API_KEY = your_groq_api_key
```

6. Deploy the application.

---

## Future Enhancements

- User authentication
- Expense tracking
- EMI Calculator
- SIP Calculator
- Loan Eligibility Calculator
- Personalized financial recommendations
- Multi-language support
- Voice-based interaction

---

## Disclaimer

FinanceBot provides educational information about personal finance and should not be considered personalized financial, investment, or tax advice. Users should consult qualified financial professionals before making financial decisions.
