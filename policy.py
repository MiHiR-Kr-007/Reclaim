from models import FailureCategory

def determine_intervention(category: str, attempt_number: int) -> dict:
    if category == FailureCategory.GATEWAY_TIMEOUT.value:
        return {"action": "silent_retry", "channel": "razorpay_retry_adapter"}
        
    elif category == FailureCategory.INSUFFICIENT_FUNDS.value:
        if attempt_number == 1:
            return {"action": "schedule_retry_and_notify", "channel": "email"}
        else:
            return {"action": "silent_retry", "channel": "razorpay_retry_adapter"}
            
    elif category == FailureCategory.AUTH_FAILED.value:
        return {"action": "request_reauthentication", "channel": "email"}
        
    return {"action": "escalate_to_human", "channel": "none"}