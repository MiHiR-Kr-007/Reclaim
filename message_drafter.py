from llm_provider import GroqProvider

llm = GroqProvider()

def draft_outreach_message(failure_category: str, channel: str) -> str:
    # Drafts a message based on the failure reason.
    system_prompt = (
        "You are a helpful customer support agent for a SaaS platform. "
        "Write a concise, friendly 2-sentence message notifying the customer of a failed payment. "
        "You may use a subtle, professional Hinglish tone. Do not invent facts."
    )
    
    user_prompt = f"Draft a message for a {channel} channel regarding a failure due to: {failure_category}."
    
    message = llm.generate_text(prompt=user_prompt, system_message=system_prompt)
    
    if "AI layer unavailable" in message:
        return "Your recent payment failed. Please check your account to update your payment method."
        
    return message