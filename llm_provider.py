import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_message: str = "") -> str:
        pass

class GroqProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[Warning] Failed to initialize Groq client: {e}")

    def generate_text(self, prompt: str, system_message: str = "") -> str:
        if not self.client:
            return "AI layer unavailable. Fallback response used."
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model="openai/gpt-oss-20b",
                temperature=0.2
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as err:
            print(f"[AI Error] Groq request failed: {err}")
            return "AI layer unavailable. Fallback response used."