import streamlit as st
import requests
import pandas as pd
from sqlalchemy.orm import Session
from models import SessionLocal, RecoveryCase, DecisionRecord
from metrics import calculate_metrics
from decision_narrator import summarize_case_history

st.set_page_config(page_title="Reclaim Engine", layout="wide")
st.title("Reclaim: AI Revenue Recovery Engine")
st.caption("Optimized to recover revenue with the fewest, fully compliant touches.")

def get_db():
    db = SessionLocal()
    try: return db
    finally: db.close()

db = get_db()

st.markdown("### Control Panel")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("Run Batch Simulator (20 Cases)"):
        with st.spinner("Simulating failed payments through the orchestrator..."):
            try:
                requests.post("http://localhost:8000/simulate/batch?batch_size=20")
                st.success("Batch processed successfully! Engine executed all compliance checks.")
            except Exception as e:
                st.error(f"Failed to reach API. Is your FastAPI server running? Error: {e}")

with col_b:
    if st.button("Simulate User Payments (Demo)"):
        with st.spinner("Simulating users clicking links and paying..."):
            try:
                res = requests.post("http://localhost:8000/simulate/recover?recovery_rate=0.4")
                data = res.json()
                st.success(f"{data['message']} Recovered ₹{data['rupees_recovered']:,.2f}!")
            except Exception as e:
                st.error(f"Failed to reach API. Error: {e}")

st.divider()

st.markdown("### Recovery Metrics")
metrics = calculate_metrics(db)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cases Detected", metrics["total_cases"])
col2.metric("Recovery Rate", f"{metrics['recovery_rate_percent']}%")
col3.metric("Total ₹ Recovered", f"₹ {metrics['rupees_recovered']:,.2f}")
col4.metric("Compliance Blocks", metrics["compliance_blocks"])
st.caption("Compliance blocks represent actions stopped by the RBI guard (e.g., AFA limits, 24h notices).")

st.divider()

st.markdown("### Case Ledger")
cases = db.query(RecoveryCase).all()

if cases:
    case_data = [{
        "Case ID": c.id,
        "State": c.state,
        "Category": c.category,
        "Attempts": c.attempts,
        "Amount (₹)": c.amount_paise / 100
    } for c in cases]
    st.dataframe(pd.DataFrame(case_data), width="stretch")

st.divider()

st.markdown("### Deep Dive: Audit Trail & AI Narration")
if cases:
    selected_case_id = st.selectbox("Select a Case ID to audit:", [c.id for c in cases])
    
    if selected_case_id:
        records = db.query(DecisionRecord).filter(DecisionRecord.case_id == selected_case_id).all()
        
        st.markdown("**AI Case Explanation:**")
        if st.button("Generate Plain-English Explanation"):
            with st.spinner("AI is reading the compliance logs..."):
                summary = summarize_case_history(records)
                st.info(summary)
        
        st.markdown("**Raw Immutable Audit Log:**")
        log_data = [{
            "Actor": r.actor,
            "Rule": r.rule_name,
            "Allowed": r.allowed,
            "Reason": r.reason,
            "Timestamp": r.created_at
        } for r in records]
        st.dataframe(pd.DataFrame(log_data), width="stretch")