from models import RecoveryCase, DecisionRecord

def check_afa_threshold(case: RecoveryCase) -> DecisionRecord:
    # Transactions over ₹15,000 require Additional Factor of Authentication (AFA)
    limit_paise = 1500000
    
    if case.amount_paise > limit_paise:
        return DecisionRecord(
            case_id=case.id,
            actor="compliance_guard",
            allowed=False,
            reason="Amount exceeds ₹15,000. Fresh AFA required, silent retry blocked."
        )
    
    return DecisionRecord(
        case_id=case.id,
        actor="compliance_guard",
        allowed=True,
        reason="Amount under ₹15,000. Standing consent applies."
    )