"""
FinanceBot - AI Personal Finance Chatbot

Flask backend that integrates the Groq API with a structured
Indian personal-finance knowledge base for domain-specific Q&A.
"""

import os
import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Groq client
# ---------------------------------------------------------------------------

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

MODEL_NAME = "llama-3.1-8b-instant"


# ---------------------------------------------------------------------------
# Structured financial knowledge base
# ---------------------------------------------------------------------------

FINANCE_KNOWLEDGE_BASE = {
    "tax_regimes": {
        "old_regime": (
            "Allows deductions under 80C up to 1.5 lakh, "
            "80D health insurance, HRA and home-loan interest."
        ),
        "new_regime": (
            "Provides lower tax slab rates, but most deductions and "
            "exemptions are not available. A standard deduction may apply "
            "for eligible salaried individuals."
        ),
    },

    "investment_instruments": {
        "PPF": (
            "Public Provident Fund has a 15-year lock-in period, "
            "government backing and tax benefits."
        ),

        "ELSS": (
            "Equity Linked Savings Scheme is a mutual fund with a "
            "3-year lock-in period and qualifies for Section 80C."
        ),

        "NPS": (
            "National Pension System is a retirement-focused investment "
            "scheme that may provide additional tax deductions."
        ),

        "FD": (
            "Fixed Deposit provides relatively predictable returns, "
            "but the interest earned is generally taxable."
        ),

        "SIP": (
            "A Systematic Investment Plan allows periodic investment "
            "into mutual funds and supports disciplined investing."
        ),

        "SGB": (
            "Sovereign Gold Bonds provide government-backed exposure "
            "to gold and may include interest income."
        ),
    },

    "budgeting_frameworks": {
        "50-30-20 rule": (
            "A common budgeting framework that allocates 50% to needs, "
            "30% to wants and 20% to savings or investments."
        ),

        "Emergency fund": (
            "An emergency fund generally contains 3 to 6 months of "
            "essential expenses in a liquid and accessible instrument."
        ),
    },

    "credit": {
        "CIBIL score": (
            "A CIBIL score ranges from 300 to 900. A score above 750 "
            "is generally considered healthy."
        ),

        "credit_utilization": (
            "Keeping credit usage below approximately 30% of the total "
            "available limit may support a healthy credit score."
        ),
    },

    "disclaimer": (
        "FinanceBot provides general educational information and is not "
        "a substitute for advice from a SEBI-registered investment adviser "
        "or qualified tax professional. Financial rules and rates may change."
    ),
}


SYSTEM_PROMPT = f"""
You are FinanceBot, a conversational assistant focused exclusively on
personal finance, with special depth in the Indian financial context.

You can answer questions about:

- Budgeting
- SIP and mutual funds
- PPF, ELSS and NPS
- Fixed deposits
- Credit cards and CIBIL scores
- Insurance
- Loans
- Tax basics
- Emergency funds

Use the following structured knowledge base when relevant:

{json.dumps(FINANCE_KNOWLEDGE_BASE, indent=2)}

Guidelines:

- Give clear and domain-specific answers.
- Use simple examples with INR amounts where useful.
- If a question is outside personal finance, politely redirect the user.
- Do not provide guaranteed investment-return claims.
- Do not directly tell users to buy a particular stock.
- Mention that personalized decisions should be discussed with a qualified adviser.
- Keep answers concise and suitable for a chatbot.
- Default currency is INR.
"""


# In-memory conversation store
conversations = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    user_message = (data.get("message") or "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({
            "error": "Please enter a message."
        }), 400

    history = conversations.setdefault(session_id, [])

    history.append({
        "role": "user",
        "content": user_message
    })

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history[-20:])

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=1024,
            temperature=0.4
        )

        reply_text = response.choices[0].message.content

    except Exception as exc:
        print("Groq API error:", exc)

        # Remove the unanswered user message
        if history:
            history.pop()

        return jsonify({
            "error": "FinanceBot is temporarily unavailable. Please try again."
        }), 500

    history.append({
        "role": "assistant",
        "content": reply_text
    })

    return jsonify({
        "reply": reply_text,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "default")

    conversations.pop(session_id, None)

    return jsonify({
        "status": "cleared"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
