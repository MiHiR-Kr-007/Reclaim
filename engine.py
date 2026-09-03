from models import CaseState, FailureCategory, RecoveryCase

ERROR_MAPPING = {
    "insufficient_fund": FailureCategory.INSUFFICIENT_FUNDS.value,
    "payment_timed_out": FailureCategory.GATEWAY_TIMEOUT.value,
    "authentication_failed": FailureCategory.AUTH_FAILED.value,
    "card_expired": FailureCategory.CARD_EXPIRED.value,
    "mandate_revoked": FailureCategory.MANDATE_REVOKED.value,
    "invoice_past_due": FailureCategory.INVOICE_OVERDUE.value
}

def diagnose_failure(error_reason: str) -> str:
    # Translates Razorpay error strings into our internal categories.
    return ERROR_MAPPING.get(error_reason, FailureCategory.UNKNOWN.value)

def transition_state(case: RecoveryCase, new_state: CaseState):
    # Defines what moves are legal.
    valid_transitions = {
        CaseState.DETECTED: [CaseState.DIAGNOSING],
        CaseState.DIAGNOSING: [CaseState.INTERVENTION_SCHEDULED, CaseState.ESCALATED],
        CaseState.INTERVENTION_SCHEDULED: [CaseState.INTERVENTION_SENT, CaseState.ABANDONED],
        CaseState.INTERVENTION_SENT: [CaseState.AWAITING_OUTCOME],
        CaseState.AWAITING_OUTCOME: [CaseState.RECOVERED, CaseState.DIAGNOSING, CaseState.ESCALATED],
        CaseState.ESCALATED: [],
        CaseState.RECOVERED: [],
        CaseState.ABANDONED: []
    }
    
    # Any state can transition to ABANDONED
    if new_state == CaseState.ABANDONED:
        case.state = new_state.value
        return

    current_state = CaseState(case.state)
    allowed_next_states = valid_transitions.get(current_state, [])
    
    if new_state in allowed_next_states:
        case.state = new_state.value
    else:
        raise ValueError(f"Illegal transition: Cannot move from {current_state.value} to {new_state.value}")