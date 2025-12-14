import os
import json
import requests
from openai import OpenAI

class LLMClient:
    def __init__(self, api_key, base_url, model, provider="openai"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.provider = provider.lower()

        self.system_prompt = (
            "You are a professional translator for Japanese Visual Novels (Galgame). "
            "Translate the following text into Simplified Chinese. "
            "Maintain the tone, style, and nuances of the characters. "
            "IMPORTANT: Do NOT translate or remove any placeholders like [[VAR_0]], [[VAR_1]]. Keep them exactly as is. "
            "Output ONLY the translated text, no explanations."
        )

        if self.provider == "openai" or self.provider == "deepseek" or self.provider == "qwen":
            # DeepSeek and Qwen are often OpenAI-compatible
            self.client = OpenAI(api_key=api_key, base_url=base_url)

        # Gemini setup (REST fallback if library not present, or use custom logic)
        # For now, we will assume OpenAI compatibility for simplicity unless Gemini is strictly different.
        # Actually, Google's OpenAI compatibility endpoint is `https://generativelanguage.googleapis.com/v1beta/openai/`
        # So we can treat Gemini as OpenAI-compatible if the user provides the correct base URL.
        # But if we want native Gemini REST, we'd add it here.
        # Let's stick to OpenAI wrapper for all for now, as it's the standard.
        elif self.provider == "gemini":
             # Google GenAI via OpenAI adapter usually
             self.client = OpenAI(
                 api_key=api_key,
                 base_url=base_url if base_url else "https://generativelanguage.googleapis.com/v1beta/openai/"
             )
        else:
             # Default fallback
             self.client = OpenAI(api_key=api_key, base_url=base_url)

    def translate(self, text, history=None, glossary=None):
        messages = [{"role": "system", "content": self.system_prompt}]

        # Inject glossary instructions if present
        if glossary:
            glossary_text = "\n".join([f"{k} -> {v}" for k, v in glossary.items()])
            messages[0]["content"] += f"\n\nGlossary (Use these strictly):\n{glossary_text}"

        # Add history
        if history:
            for h in history[-5:]:
                messages.append({"role": "user", "content": h['original']})
                messages.append({"role": "assistant", "content": h['translated']})

        messages.append({"role": "user", "content": text})

        try:
            # Special handling for different providers if needed parameters differ
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
            }

            # Gemini OpenAI adapter sometimes requires max_tokens
            if self.provider == "gemini":
                params["max_tokens"] = 1024

            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error: {str(e)}]"
