import json
from models import FailureCategory
from llm_provider import GroqProvider

llm = GroqProvider()

def get_baseline_strategy(category: str, attempt_number: int) -> dict:
    if category == FailureCategory.GATEWAY_TIMEOUT.value:
        return {"action": "silent_retry", "channel": "razorpay_retry_adapter"}
        
    elif category == FailureCategory.INSUFFICIENT_FUNDS.value:
        if attempt_number == 1:
            return {"action": "schedule_retry_and_notify", "channel": "email"}
        else:
            return {"action": "silent_retry", "channel": "razorpay_retry_adapter"}
            
    elif category == FailureCategory.AUTH_FAILED.value:
        return {"action": "request_reauthentication", "channel": "email"}

    elif category == FailureCategory.INVOICE_OVERDUE.value:
        return {"action": "request_promise_to_pay", "channel": "email"}
        
    return {"action": "escalate_to_human", "channel": "none"}

def determine_intervention(category: str, attempt_number: int, amount: int, error_reason: str, use_ai: bool = True) -> dict:
    baseline = get_baseline_strategy(category, attempt_number)
    baseline["message"] = "Your payment failed. Please update your card."
    baseline["reasoning"] = "Heuristic baseline applied."
    
    if not use_ai:
        return baseline
        
    system_message = (
        "You are an AI Revenue Recovery Strategist for a Fintech platform. "
        "Your job is to review a failed payment context and the heuristic 'baseline' strategy, "
        "and output a JSON object to optimize the recovery action.\n"
        "Return ONLY valid JSON in this exact format:\n"
        "{\n"
        "  \"action\": \"<silent_retry|schedule_retry_and_notify|request_reauthentication|request_promise_to_pay|escalate_to_human>\",\n"
        "  \"channel\": \"<email|mock_sms|hinglish_voice|none>\",\n"
        "  \"message\": \"<A short, 1-2 sentence personalized message to the user>\",\n"
        "  \"reasoning\": \"<1-sentence explanation of why you chose this action over or agreeing with the baseline>\"\n"
        "}"
    )
    
    prompt = (
        f"Context:\n"
        f"- Failure Category: {category}\n"
        f"- Raw Error: {error_reason}\n"
        f"- Attempt Number: {attempt_number}\n"
        f"- Amount (paise): {amount}\n"
        f"- Baseline Strategy Action: {baseline['action']}\n"
        f"- Baseline Channel: {baseline['channel']}\n\n"
        f"Decide if you should stick to the baseline or optimize it. Provide the JSON."
    )
    
    response_text = llm.generate_text(prompt=prompt, system_message=system_message)
    
    try:
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        ai_decision = json.loads(clean_text)
        
        for key in ["action", "channel", "message", "reasoning"]:
            if key not in ai_decision:
                return baseline
                
        return ai_decision
    except Exception as e:
        print(f"[Warning] Failed to parse AI decision, falling back to baseline. Error: {e}")
        return baseline