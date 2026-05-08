"""
MAIN ORCHESTRATOR
This script runs the entire automation pipeline
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trends.google_trends_scraper import GoogleTrendsScraper
from scripts.ai.gemini_generator import GeminiContentGenerator
from scripts.upload.github_uploader import GitHubUploader
from scripts.whatsapp.whapi_poster import WhapiPoster


class AutomationOrchestrator:
    def __init__(self):
        self.data_dir = 'data'
        self.ensure_data_directory()

        print("🔧 Initializing automation system...\n")

        self.google_trends = GoogleTrendsScraper()
        self.content_gen = GeminiContentGenerator()
        self.uploader = GitHubUploader()
        self.poster = WhapiPoster()

        print("✅ All components initialized!\n")

    def ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def step_1_scrape_trends(self):
        print("="*60)
        print("STEP 1: SCRAPING TRENDING TOPICS")
        print("="*60 + "\n")

        print("📡 Scraping Google Trends...")
        google_summary, google_data = self.google_trends.get_comprehensive_trends()

        trends_data = {
            'google': google_data,
            'timestamp': datetime.now().isoformat()
        }

        with open(f'{self.data_dir}/trends_data.json', 'w') as f:
            json.dump(trends_data, f, indent=2)

        print("\n✅ Trend scraping complete!\n")
        return google_summary, trends_data

    def step_2_generate_content(self, trends_summary):
        print("="*60)
        print("STEP 2: GENERATING VIRAL CONTENT WITH GEMINI AI")
        print("="*60 + "\n")

        print("🤖 Gemini is analyzing trends and creating content...")

        content = self.content_gen.generate_viral_content(trends_summary)

        if not content:
            raise Exception("Failed to generate content with Gemini")

        with open(f'{self.data_dir}/generated_content.json', 'w') as f:
            json.dump(content, f, indent=2)

        print("\n✅ Content generation complete!")
        print(f"\n📝 CAPTION PREVIEW:\n{content['viral_caption']}\n")
        print(f"🎨 PROMPT PREVIEW:\n{content['image_prompt'][:200]}...\n")

        return content

    def step_3_send_to_kaggle(self, content):
        print("="*60)
        print("STEP 3: PREPARING FOR KAGGLE IMAGE GENERATION")
        print("="*60 + "\n")

        kaggle_input = {
            'positive_prompt': content['image_prompt'],
            'negative_prompt': content['negative_prompt'],
            'style': content['style'],
            'timestamp': datetime.now().isoformat()
        }

        with open(f'{self.data_dir}/kaggle_input.json', 'w') as f:
            json.dump(kaggle_input, f, indent=2)

        print("✅ Kaggle input file created!")
        print(f"📁 Location: {self.data_dir}/kaggle_input.json\n")

        return 'output/generated_image.png'

    def step_4_upload_image(self, image_path):
        print("="*60)
        print("STEP 4: UPLOADING IMAGE TO GITHUB CDN")
        print("="*60 + "\n")

        if not os.path.exists(image_path):
            print(f"⚠️  Image not found at: {image_path}")
            return None

        print("📤 Uploading to GitHub...")

        result = self.uploader.upload_image(image_path)

        if not result['success']:
            raise Exception(f"Upload failed: {result.get('error')}")

        print(f"\n✅ Image uploaded successfully!")
        print(f"🔗 URL: {result['url']}\n")

        return result['url']

    def step_5_post_to_whatsapp(self, image_url, content):
        print("="*60)
        print("STEP 5: POSTING TO WHATSAPP CHANNEL")
        print("="*60 + "\n")

        full_caption = f"{content['viral_caption']}\n\n{content['hashtags']}"

        print("📱 Posting to WhatsApp Channel...")

        result = self.poster.post_to_channel(image_url, full_caption)

        if not result['success']:
            raise Exception(f"Posting failed: {result.get('error')}")

        print(f"\n✅ Successfully posted to WhatsApp Channel!")
        print(f"📨 Message ID: {result['message_id']}\n")

        return result

    def run_full_pipeline(self):
        print("\n" + "="*60)
        print("🚀 STARTING AI WHATSAPP AUTOMATION PIPELINE")
        print("="*60 + "\n")

        try:
            trends_summary, trends_data = self.step_1_scrape_trends()
            content = self.step_2_generate_content(trends_summary)
            expected_image_path = self.step_3_send_to_kaggle(content)

            print("⏸️  PIPELINE PAUSED - Waiting for Kaggle image generation")

            state = {
                'step': 'waiting_for_kaggle',
                'image_path': expected_image_path,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }

            with open(f'{self.data_dir}/pipeline_state.json', 'w') as f:
                json.dump(state, f, indent=2)

            return state

        except Exception as e:
            print(f"\n❌ PIPELINE FAILED: {e}")
            import traceback
            traceback.print_exc()
            return None

    def continue_pipeline(self):
        print("\n" + "="*60)
        print("▶️  CONTINUING PIPELINE")
        print("="*60 + "\n")

        with open(f'{self.data_dir}/pipeline_state.json', 'r') as f:
            state = json.load(f)

        try:
            image_url = self.step_4_upload_image(state['image_path'])

            if not image_url:
                print("❌ Image not found. Generate it on Kaggle first!")
                return

            result = self.step_5_post_to_whatsapp(image_url, state['content'])

            print("\n" + "="*60)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*60 + "\n")

        except Exception as e:
            print(f"\n❌ CONTINUATION FAILED: {e}")
            import traceback
            traceback.print_exc()


def main():
    orchestrator = AutomationOrchestrator()

    if len(sys.argv) > 1 and sys.argv[1] == '--continue':
        orchestrator.continue_pipeline()
    else:
        orchestrator.run_full_pipeline()


if __name__ == "__main__":
    main()
