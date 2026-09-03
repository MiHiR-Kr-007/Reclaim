from llm_provider import GroqProvider
from models import DecisionRecord

llm = GroqProvider()

def summarize_case_history(records: list[DecisionRecord]) -> str:
    # Convert an audit trail to a plain-English explanation.

    if not records:
        return "No decisions have been recorded for this case yet."
        
    # Format the logs into a readable string for the AI
    history_text = "\n".join([
        f"- Checked {r.rule_name}: Allowed={r.allowed} (Reason: {r.reason})" 
        for r in records
    ])
    
    system_prompt = (
        "You are a compliance audit summarizer. Read the following system logs "
        "and explain why the system took its final action in one clear, plain-English paragraph."
    )
    
    summary = llm.generate_text(prompt=history_text, system_message=system_prompt)
    
    if "AI layer unavailable" in summary:
        return "Audit log summary unavailable. Please check the raw compliance logs."
        
    return summary