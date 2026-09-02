from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import SessionLocal, RecoveryCase, CaseState, DecisionRecord
from engine import diagnose_failure, transition_state
from policy import determine_intervention
from compliance import check_afa_threshold
from adapters import MockSmsAdapter

app = FastAPI()
sms_adapter = MockSmsAdapter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/webhooks/razorpay")
def receive_webhook(event: dict, db: Session = Depends()):
    error_reason = event.get("payload", {}).get("payment", {}).get("entity", {}).get("error_reason", "unknown")
    amount = event.get("amount", 0)
    
    case = RecoveryCase(amount_paise=amount)
    db.add(case)
    db.commit()

    transition_state(case, CaseState.DIAGNOSING)
    case.category = diagnose_failure(error_reason)
    db.commit()

    intervention = determine_intervention(case.category, attempt_number=1) 
    
    compliance_decision = check_afa_threshold(case)
    db.add(compliance_decision) 
    
    if compliance_decision.allowed:
        if intervention["channel"] in ["email", "mock_sms"]:
            sms_adapter.send(case.id, "Your payment failed. Please update your card.")
        
        transition_state(case, CaseState.ESCALATED) 
    else:
        transition_state(case, CaseState.ESCALATED)
    
    db.commit()
    
    return {
        "status": "Processed", 
        "case_id": case.id, 
        "category": case.category,
        "action_taken": intervention["action"],
        "compliance_allowed": compliance_decision.allowed
    }