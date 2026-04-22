import os
import openai
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

class GPTPasswordGenerator:
    def __init__(self, api_key=None, model="text-davinci-003"):
        self.api_key = api_key or os.getenv("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")
        openai.api_key = self.api_key
        self.model = model

    def generate_passwords(self, keywords, num_passwords=1000, batch_size=10):
        """
        Generate password candidates using GPT
        """
        generated_passwords = []

        print("[INFO] Starting GPT password generation...")

        for i in tqdm(range(0, len(keywords), batch_size)):
            batch_keywords = keywords[i:i+batch_size]

            prompt = self._build_prompt(batch_keywords)

            try:
                response = openai.Completion.create(
                    model=self.model,
                    prompt=prompt,
                    max_tokens=100,
                    temperature=0.7,
                    n=1
                )

                text = response["choices"][0]["text"]

                passwords = self._parse_passwords(text)
                generated_passwords.extend(passwords)

            except Exception as e:
                print(f"[ERROR] GPT generation failed: {e}")
                continue

            if len(generated_passwords) >= num_passwords:
                break

        print(f"[INFO] Generated {len(generated_passwords)} passwords")
        return generated_passwords[:num_passwords]

    def _build_prompt(self, keywords):
        keyword_str = ", ".join(keywords)

        return f"""
Generate a list of realistic, commonly used passwords using these keywords:
{keyword_str}

Rules:
- Mix words, numbers, and common patterns
- Include variations like 123, !, @
- Output only passwords, one per line

Passwords:
"""

    def _parse_passwords(self, text):
        lines = text.strip().split("\n")
        passwords = []

        for line in lines:
            clean = line.strip().replace("-", "").replace("*", "")
            if clean:
                passwords.append(clean)

        return passwords

    def save_passwords(self, passwords, output_path):
        df = pd.DataFrame({"password": passwords})
        df.to_csv(output_path, index=False)
        print(f"[INFO] Saved generated passwords to {output_path}")