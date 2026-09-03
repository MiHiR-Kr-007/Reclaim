import random
from datetime import datetime

FAILURE_REASONS = (
    ["insufficient_fund"] * 35 +
    ["payment_timed_out"] * 20 +
    ["authentication_failed"] * 20 +
    ["card_expired"] * 15 +
    ["mandate_revoked"] * 10
)

class BatchSimulator:
    @staticmethod
    def generate(n: int = 10) -> list[dict]:
        events = []
        for i in range(1, n + 1):
            amount = random.choice([49900, 99900, 149900, 1800000, 2500000])
            reason = random.choice(FAILURE_REASONS)
            
            event = {
                "event": "payment.failed",
                "amount": amount,
                "created_at": int(datetime.utcnow().timestamp()),
                "payload": {
                    "payment": {
                        "entity": {
                            "id": f"pay_synth_{i:04d}",
                            "amount": amount,
                            "currency": "INR",
                            "status": "failed",
                            "error_reason": reason,
                            "error_description": f"Synthetic failure: {reason}"
                        }
                    }
                }
            }
            events.append(event)
        return events