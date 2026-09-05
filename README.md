# Reclaim: Hybrid Agentic Revenue Recovery Engine 

**Built for the Razorpay Buildathon: AI Revenue Recovery Track**

Reclaim is an intelligent, RBI-compliant revenue recovery engine. It detects payments at risk (failed subscriptions, checkout drop-offs, overdue B2B invoices), uses an LLM Agent to strategize the best recovery action, and executes a bounded workflow—all while proving exactly *why* it acted via an immutable audit trail.

---

## The Problem
Revenue loss rarely happens in one clean step. A payment degrades due to insufficient funds, an expired mandate, or a gateway timeout. 
Most standard recovery tools use brute-force heuristic retries. This leads to two massive problems:
1. **Low Conversion:** Blasting generic "Your payment failed" emails ignores context.
2. **Compliance Risk:** Blindly retrying cards can violate RBI regulations (e.g., the ₹15,000 AFA limit or the 24-hour pre-debit notice mandate).

## Our Solution: The Bounded Hybrid Agent
Reclaim solves this by marrying **Agentic AI** with a **Deterministic Compliance State Machine**. 

### 1. The Revenue Recovery Strategist (AI Layer)
When a payment fails, Reclaim doesn't just guess. It feeds the failure context (Category, Error string, Attempt history, Amount) into an LLM Agent (powered by Groq). The Agent acts as a Revenue Recovery Strategist to:
- Choose the optimal recovery action (e.g., `silent_retry`, `request_promise_to_pay`).
- Draft hyper-personalized, context-aware outreach messages (e.g., Hinglish messaging, empathy-driven prompts).

### 2. The RBI Compliance Guard (Safety Layer)
You cannot give an LLM unchecked access to financial workflows. Every decision the AI makes is intercepted by our Compliance Guard before execution. 
It evaluates the AI's action against hardcoded RBI rules:
- **Pre-Debit Notice:** Blocks recurring debits unless the 24h advance notice has been sent.
- **AFA Threshold:** Blocks silent retries for amounts > ₹15,000, enforcing fresh authentication.
- **Max Attempts & Cooldown:** Enforces responsible collection limits.

### 3. Immutable Audit Trail
Every single AI decision and Compliance Guard evaluation creates a `DecisionRecord`. Reclaim doesn't just recover money; it proves exactly *why* it did so in a plain-English, fully auditable ledger.

---

## 🛠 Tech Stack & Architecture Justification
**Stack:** Python, FastAPI, SQLite, Streamlit, Groq LLM API, Razorpay API.

**Why a Modular Monolith?**
We deliberately avoided microservices and complex infrastructure. A single FastAPI process backed by SQLite allows for maximum velocity, zero-cost local deployment, and high reliability. The architecture is modular *internally*, allowing new adapters (Twilio, Razorpay) and AI models to be plugged in effortlessly.

---

## Key Features Demonstrated
- **Agentic Decision Making:** Contextual recovery logic vs. static if/else blocks.
- **Razorpay Integration:** Real test-mode authentication and payload construction in the `RazorpayRetryAdapter`.
- **Batch Simulator:** Generates synthetic failures matching real-world distributions (e.g., 35% insufficient funds, 20% timeouts) and pushes them through the real engine.
- **Live Recovery Dashboard:** A Streamlit app showing live Recovery Rates, ₹ Recovered, Compliance Blocks, and a Deep Dive AI Audit Trail.

---

## 💻 How to Run Locally

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_key
   RAZORPAY_KEY_ID=your_razorpay_test_key_id
   RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret
   ```

3. **Start the Core Engine:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Launch the Dashboard (in a new terminal):**
   ```bash
   streamlit run dashboard.py
   ```

5. **Run the Demo:**
   - In the Streamlit dashboard, click **Run Batch Simulator** to watch the AI process 100 failed payments in real-time.
   - Click **Simulate User Payments** to watch the Recovery Rate skyrocket!