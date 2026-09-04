from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import SessionLocal, RecoveryCase, CaseState, DecisionRecord
from engine import diagnose_failure, transition_state
from policy import determine_intervention
from compliance import ComplianceGuard
from adapters import MockSmsAdapter, RazorpayRetryAdapter
from simulator import BatchSimulator
from metrics import calculate_metrics

app = FastAPI()
sms_adapter = MockSmsAdapter()
# razorpay_adapter = RazorpayRetryAdapter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def process_recovery_event(event: dict, db: Session) -> dict:
    error_reason = event.get("payload", {}).get("payment", {}).get("entity", {}).get("error_reason", "unknown")
    amount = event.get("amount", 0)
    
    # 1. Detect & Create
    case = RecoveryCase(amount_paise=amount)
    db.add(case)
    db.commit()

    # 2. Diagnose
    transition_state(case, CaseState.DIAGNOSING)
    case.category = diagnose_failure(error_reason)
    db.commit()

    # 3. Policy Decision
    intervention = determine_intervention(case.category, attempt_number=1) 
    
    # 4. Compliance Guard
    compliance_decisions = ComplianceGuard.evaluate_all(case, intervention["action"])
    for decision in compliance_decisions:
        db.add(decision)
    
    is_allowed = all(d.allowed for d in compliance_decisions)
    
    # 5. Execute or Block
    if is_allowed:
        transition_state(case, CaseState.INTERVENTION_SCHEDULED)
        if intervention["channel"] in ["email", "mock_sms"]:
            sms_adapter.send(case.id, "Your payment failed. Please update your card.")
        transition_state(case, CaseState.INTERVENTION_SENT)
    else:
        transition_state(case, CaseState.ESCALATED)
    
    db.commit()
    
    return {
        "case_id": case.id, 
        "category": case.category,
        "action_taken": intervention["action"],
        "compliance_allowed": is_allowed
    }

@app.post("/webhooks/razorpay")
def receive_webhook(event: dict, db: Session = Depends(get_db)):
    return process_recovery_event(event, db)

@app.post("/simulate/batch")
def simulate_batch(batch_size: int = 20, db: Session = Depends(get_db)):
    events = BatchSimulator.generate(n=batch_size)
    results = []
    
    for event in events:
        result = process_recovery_event(event, db)
        results.append(result)
        
    return {
        "message": f"Processed {batch_size} synthetic events",
        "results": results
    }

@app.post("/simulate/recover")
def simulate_recover(recovery_rate: float = 0.4, db: Session = Depends(get_db)):
    import random
    from datetime import datetime
    
    # Find cases that received an intervention
    eligible_cases = db.query(RecoveryCase).filter(
        RecoveryCase.state == CaseState.INTERVENTION_SENT.value
    ).all()
    
    recovered_count = 0
    recovered_amount = 0
    
    for case in eligible_cases:
        if random.random() < recovery_rate:
            transition_state(case, CaseState.AWAITING_OUTCOME)
            transition_state(case, CaseState.RECOVERED)
            case.recovered_at = datetime.utcnow()
            case.attempts += 1
            recovered_count += 1
            recovered_amount += case.amount_paise
            
    db.commit()
    return {
        "message": f"Simulated recovery for {recovered_count} cases.",
        "rupees_recovered": recovered_amount / 100
    }

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return calculate_metrics(db)

@app.get("/cases")
def get_all_cases(db: Session = Depends(get_db)):
    cases = db.query(RecoveryCase).all()
    return cases