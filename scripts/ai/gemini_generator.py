"""
Groq AI Content Generator
Fast, free, generous quota - perfect replacement for Gemini
"""

import json
import random
import os
import requests
from datetime import datetime
from config.config import VISUAL_STYLES
from scripts.ai.reference_analyzer import ReferenceAnalyzer


class GeminiContentGenerator:
    def __init__(self, reference_image_path='assets/reference_face.png'):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"

        self.ref_analyzer = ReferenceAnalyzer(reference_image_path)
        self.base_character = self.ref_analyzer.get_base_character_prompt()
        self.character_components = self.ref_analyzer.get_detailed_prompt_components()

    def create_system_prompt(self):
        return f"""You are a VIRAL VISUAL CONTENT STRATEGIST for a WhatsApp AI channel.

Your mission: Create highly engaging, shareable AI-generated content.

## REFERENCE CHARACTER (MUST MAINTAIN IN EVERY IMAGE):
{json.dumps(self.character_components, indent=2)}

## BASE CHARACTER DESCRIPTION:
{self.base_character}

## CRITICAL REQUIREMENTS:

Always include base character description in image_prompt.
Make captions emotional, engaging, with emojis.
Image prompt must be ultra realistic, cinematic quality.

## OUTPUT FORMAT (STRICT JSON ONLY - NO OTHER TEXT):

{{
  "trend_title": "The specific trend you are addressing",
  "viral_caption": "The WhatsApp caption with emojis",
  "image_prompt": "Complete prompt with base character plus scenario",
  "negative_prompt": "blurry face, deformed eyes, extra fingers, low quality, duplicate face, distorted hair, cartoon, bad anatomy, text, watermark",
  "style": "The visual style used",
  "hashtags": "#AI #Technology #Future #Pakistan",
  "reasoning": "Why this will be viral"
}}

Return ONLY valid JSON. No markdown, no explanation, just JSON."""

    def generate_viral_content(self, trends_summary):
        selected_style = random.choice(VISUAL_STYLES)

        user_prompt = f"""## TRENDING TOPICS TODAY:
{trends_summary}

## SELECTED VISUAL STYLE: {selected_style}

Create ONE highly viral WhatsApp post. The character MUST match:
{self.base_character}

Generate JSON response now."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.create_system_prompt()},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.8
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                print(f"❌ Groq API error: {response.status_code} — {response.text}")
                return None

            response_text = response.json()["choices"][0]["message"]["content"].strip()

            # Clean JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            content = json.loads(response_text)
            content['generated_at'] = datetime.now().isoformat()
            content['base_character'] = self.base_character

            print(f"✅ Content generated via Groq!")
            return content

        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
