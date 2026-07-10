"""
FinanceBot - AI Personal Finance Chatbot
Flask backend that integrates Anthropic's Claude API with a structured
Indian personal-finance knowledge base for domain-specific Q&A.
"""

import os
import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from groq import groq

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Anthropic client
# ---------------------------------------------------------------------------
# Set your key as an environment variable before running:
#   export ANTHROPIC_API_KEY="sk-ant-..."          (mac/linux)
#   setx ANTHROPIC_API_KEY "sk-ant-..."             (windows)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL_NAME = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Structured financial knowledge base
# ---------------------------------------------------------------------------
# This gives the model a grounded, India-specific frame of reference so
# answers stay accurate and domain-specific rather than generic.
FINANCE_KNOWLEDGE_BASE = {
    "tax_regimes": {
        "old_regime": "Allows deductions under 80C (up to 1.5L), 80D (health "
                       "insurance), HRA, home loan interest (24b), etc.",
        "new_regime": "Lower slab rates, but most deductions/exemptions are "
                       "not available (standard deduction of 75,000 for "
                       "salaried individuals is allowed under the new regime).",
    },
    "investment_instruments": {
        "PPF": "Public Provident Fund - 15 year lock-in, EEE tax status, "
               "sovereign-backed, current rate revised quarterly.",
        "ELSS": "Equity Linked Savings Scheme - mutual fund with 3 year "
                "lock-in, qualifies for 80C, market-linked returns.",
        "NPS": "National Pension System - retirement-focused, additional "
               "80CCD(1B) deduction of 50,000 over and above 80C.",
        "FD": "Fixed Deposit - guaranteed returns, interest is taxable as "
              "per slab, useful for short-term capital protection.",
        "SIP": "Systematic Investment Plan - disciplined periodic investing "
               "into mutual funds, benefits from rupee-cost averaging.",
        "SGB": "Sovereign Gold Bonds - government-backed gold exposure, "
               "interest income plus tax-free capital gains on maturity.",
    },
    "budgeting_frameworks": {
        "50-30-20 rule": "50% needs, 30% wants, 20% savings/investments - a "
                          "commonly used starting framework, adaptable to "
                          "individual circumstances.",
        "Emergency fund": "General guidance is 3-6 months of essential "
                           "expenses kept in a liquid instrument like a "
                           "savings account or liquid mutual fund.",
    },
    "credit": {
        "CIBIL score": "Ranges 300-900, above 750 is generally considered "
                        "healthy for loan/credit card approval.",
        "credit_utilization": "Keeping usage below ~30% of the total credit "
                               "limit is generally favorable for score health.",
    },
    "disclaimer": (
        "FinanceBot provides general educational information about personal "
        "finance concepts and is not a substitute for advice from a SEBI-"
        "registered investment adviser or a qualified tax professional. "
        "Figures like tax slabs and interest rates change; always verify "
        "current values before acting."
    ),
}

SYSTEM_PROMPT = f"""You are FinanceBot, a conversational assistant focused
exclusively on personal finance, with special depth in the Indian financial
context (tax regimes, PPF/ELSS/NPS, UPI, CIBIL, mutual funds, insurance,
budgeting).

Ground your answers in this structured knowledge base where relevant:
{json.dumps(FINANCE_KNOWLEDGE_BASE, indent=2)}

Guidelines:
- Give clear, contextual, domain-specific answers to financial questions.
- Use concrete numbers/examples where useful (₹ amounts, %, timelines).
- If a question is outside personal finance, politely redirect the user
  back to finance topics.
- Never give a definitive "you should buy X" recommendation for specific
  stocks/instruments; frame guidance as general educational information and
  suggest consulting a certified advisor for personalized decisions.
- Keep responses concise and well-structured (short paragraphs / bullet
  points), suited for a chat interface.
- Default currency is INR (₹) unless the user specifies otherwise.
"""

# In-memory conversation store, keyed by session id (simple demo storage)
conversations = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = conversations.setdefault(session_id, [])
    history.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history[-20:],  # keep last 20 turns for context window
        )
        reply_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"API error: {exc}"}), 500

    history.append({"role": "assistant", "content": reply_text})

    return jsonify({
        "reply": reply_text,
        "timestamp": datetime.utcnow().isoformat(),
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    session_id = (request.get_json(force=True) or {}).get("session_id", "default")
    conversations.pop(session_id, None)
    return jsonify({"status": "cleared"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
