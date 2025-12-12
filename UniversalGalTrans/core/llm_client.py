import os
from openai import OpenAI
import json

class LLMClient:
    def __init__(self, api_key, base_url="https://api.openai.com/v1", model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system_prompt = (
            "You are a professional translator for Japanese Visual Novels (Galgame). "
            "Translate the following text into Simplified Chinese. "
            "Maintain the tone, style, and nuances of the characters. "
            "IMPORTANT: Do NOT translate or remove any placeholders like [[VAR_0]], [[VAR_1]]. Keep them exactly as is. "
            "Output ONLY the translated text, no explanations."
        )

    def translate(self, text, history=None, glossary=None):
        """
        Translate text using the configured LLM.

        Args:
            text (str): The Japanese text to translate.
            history (list): List of previous messages for context (optional).
            glossary (dict): Key-value pairs of terms to force (optional).
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # Inject glossary instructions if present
        if glossary:
            glossary_text = "\n".join([f"{k} -> {v}" for k, v in glossary.items()])
            messages[0]["content"] += f"\n\nGlossary (Use these strictly):\n{glossary_text}"

        # Add history if present (limit to last 5 entries to save tokens)
        if history:
            for h in history[-5:]:
                messages.append({"role": "user", "content": h['original']})
                messages.append({"role": "assistant", "content": h['translated']})

        # Add current message
        messages.append({"role": "user", "content": text})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error: {str(e)}]"
