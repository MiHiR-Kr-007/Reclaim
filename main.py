from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import SessionLocal, RecoveryCase, CaseState
from engine import diagnose_failure, transition_state

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/webhooks/razorpay")
def receive_webhook(event: dict, db: Session = Depends()):
    error_reason = event.get("payload", {}).get("payment", {}).get("entity", {}).get("error_reason", "unknown")
    
    case = RecoveryCase(amount_paise=event.get("amount", 0))
    db.add(case)
    db.commit()

    # Trigger Diagnosis
    transition_state(case, CaseState.DIAGNOSING)
    case.category = diagnose_failure(error_reason)
    db.commit()
    
    return {"status": "Case created", "case_id": case.id, "category": case.category}