from models import CaseState, FailureCategory, RecoveryCase

ERROR_MAPPING = {
    "insufficient_fund": FailureCategory.INSUFFICIENT_FUNDS.value,
    "payment_timed_out": "GATEWAY_TIMEOUT",
    "authentication_failed": "AUTH_FAILED"
}

def diagnose_failure(error_reason: str) -> str:
    return ERROR_MAPPING.get(error_reason, FailureCategory.UNKNOWN.value)

def transition_state(case: RecoveryCase, new_state: CaseState):
    valid_transitions = {
        CaseState.DETECTED: [CaseState.DIAGNOSING],
        CaseState.DIAGNOSING: [CaseState.ESCALATED]
    }
    if new_state in valid_transitions.get(CaseState(case.state), []):
        case.state = new_state.value
    else:
        raise ValueError(f"Illegal transition from {case.state} to {new_state}")