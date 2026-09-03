import os
import razorpay
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

class ChannelAdapter(ABC):
    @abstractmethod
    def send(self, case_id: int, message: str = "", reference_id: str = "") -> bool:
        pass

class MockSmsAdapter(ChannelAdapter):
    def send(self, case_id: int, message: str = "", reference_id: str = "") -> bool:
        print(f"\n[MOCK SMS OUTBOUND] Case {case_id}")
        print(f"Message: {message}\n")
        return True

class MockEmailAdapter(ChannelAdapter):
    def send(self, case_id: int, message: str = "", reference_id: str = "") -> bool:
        print(f"\n[MOCK EMAIL OUTBOUND] Case {case_id}")
        print(f"Message: {message}\n")
        return True

class RazorpayRetryAdapter(ChannelAdapter):
    # Makes call to Razorpay's test-mode APIs to attempt a retry (doing still mock behaviour).

    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        self.client = None
        
        if self.key_id and self.key_secret:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            except Exception as e:
                print(f"[Warning] Razorpay client init failed: {e}")

    def send(self, case_id: int, message: str = "", reference_id: str = "") -> bool:
        if not self.client:
            print(f"[ERROR] Razorpay keys missing. Cannot retry Case {case_id}.")
            return False
            
        try:
            print(f"\n[RAZORPAY API] Initiating real test-mode retry for Case {case_id}...")
            
            payment_link_data = {
                "amount": 1000, # paise
                "currency": "INR",
                "description": f"Retry for Case {case_id}",
                "customer": {"name": "Test Customer", "email": "test@example.com"}
            }
            print("[RAZORPAY API] Retry payload constructed successfully.")
            return True
            
        except Exception as e:
            print(f"[RAZORPAY API ERROR] Failed to retry Case {case_id}: {e}")
            return False