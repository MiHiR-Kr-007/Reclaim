class MockSmsAdapter:
    def send(self, case_id: int, message: str) -> bool:
        print(f"***")
        print(f"[MOCK SMS OUTBOUND] Case {case_id}")
        print(f"Message: {message}")
        print(f"***")
        return True

