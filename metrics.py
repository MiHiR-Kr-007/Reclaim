from sqlalchemy.orm import Session
from sqlalchemy import func
from models import RecoveryCase, CaseState, DecisionRecord

def calculate_metrics(db: Session) -> dict:
    # Total and Recovered counts
    total_cases = db.query(RecoveryCase).count()
    recovered_cases_query = db.query(RecoveryCase).filter(RecoveryCase.state == CaseState.RECOVERED.value)
    recovered_cases_count = recovered_cases_query.count()

    # Recovery Rate = RECOVERED cases / total cases
    recovery_rate = (recovered_cases_count / total_cases * 100) if total_cases > 0 else 0

    # Recovered = sum of amount_paise for RECOVERED cases
    paise_recovered = db.query(func.sum(RecoveryCase.amount_paise)).filter(
        RecoveryCase.state == CaseState.RECOVERED.value
    ).scalar() or 0
    rupees_recovered = paise_recovered / 100

    # Averages for recovered cases
    total_time_seconds = 0
    total_attempts = 0
    recovered_records = recovered_cases_query.all()
    
    for case in recovered_records:
        if case.recovered_at and case.created_at:
            total_time_seconds += (case.recovered_at - case.created_at).total_seconds()
        total_attempts += case.attempts
        
    avg_time_to_recovery = (total_time_seconds / recovered_cases_count) if recovered_cases_count > 0 else 0
    avg_attempts = (total_attempts / recovered_cases_count) if recovered_cases_count > 0 else 0

    compliance_blocks = db.query(DecisionRecord).filter(
        DecisionRecord.actor == "compliance_guard",
        DecisionRecord.allowed == False
    ).count()

    return {
        "total_cases": total_cases,
        "recovered_cases_count": recovered_cases_count,
        "recovery_rate_percent": round(recovery_rate, 2),
        "rupees_recovered": rupees_recovered,
        "avg_time_to_recovery_seconds": round(avg_time_to_recovery, 2),
        "avg_attempts_per_recovered": round(avg_attempts, 2),
        "compliance_blocks": compliance_blocks
    }