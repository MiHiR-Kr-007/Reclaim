# Reclaim: AI Revenue Recovery Engine

Most recovery bots are optimized to maximize contact attempts. Reclaim is optimized to recover revenue with the fewest, best-timed, fully compliant touches—and can prove, after the fact, exactly why it acted or didn't.

## The AI Boundary

Allowing an LLM to make financial or compliance decisions creates significant liability. Therefore, the AI is strictly bounded:

- **AI DOES NOT** decide whether or when to retry a payment.
- **AI DOES NOT** evaluate compliance rules.
- **AI IS ONLY USED FOR:**
  1. Fallback classification of ambiguous error strings.
  2. Drafting contextual outreach messages.
  3. Narrating immutable audit logs into plain English for the dashboard.

## Grounded Compliance Guard

Standard recovery engines can aggressively retry failed payments. Reclaim evaluates every action against applicable RBI e-mandate rules before execution:

- **Pre-Debit Notice:** Blocks recurring debits unless the required advance notice has been sent.
- **AFA Threshold:** Blocks silent retries for amounts above ₹15,000, enforcing fresh authentication where required.
- **Max Attempts & Cooldown:** Enforces responsible collection limits and cooldown periods to prevent excessive or repetitive recovery attempts.

Every evaluation—whether passed or failed—creates an immutable `DecisionRecord` for complete auditability.

## Architecture Justification

**Tech Stack:** Python, FastAPI, SQLite, Streamlit.

### Why a Modular Monolith?

We deliberately avoided microservices, message queues, and Kubernetes. At this scale, there is no need for independent service scaling or complex team boundaries.

A single FastAPI process backed by SQLite is the deliberately correct engineering choice for:

- Fast development and iteration
- Low operational complexity
- High reliability
- Zero-cost local deployment
- Straightforward debugging and observability

The architecture remains modular internally, allowing new policies and event types to be added without introducing unnecessary infrastructure complexity.

### B2B Extensibility

To demonstrate the modularity of the state machine, Reclaim was extended to support B2B `InvoiceOverdueEvent` scenarios.

By adding a **Promise-to-Pay policy strategy**, the new B2B workflow reuses the entire core engine and compliance guard without modifying the underlying recovery infrastructure.

This demonstrates that the architecture can support additional revenue-recovery use cases while keeping the core decision and compliance layers consistent.

### Batch Simulator vs. Live Test

The system includes a batch simulator that generates events using a realistic failure distribution, such as:

- 35% insufficient funds
- 20% payment timeouts
- Other realistic payment failure categories

These synthetic events are processed through the **exact same orchestrator** used by live webhooks.

This ensures that simulator results are not based on a separate or simplified code path, allowing the resulting recovery metrics to accurately represent how the production workflow behaves.

## How to Run
1. `pip install -r requirements.txt`
2. Configure `.env` with Groq and Razorpay test keys.
3. Start the engine: `uvicorn main:app --reload`
4. Start the dashboard: `streamlit run dashboard.py`