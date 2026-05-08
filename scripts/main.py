"""
MAIN ORCHESTRATOR — with Firebase integration
Place at: scripts/main.py
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
from scripts.firebase_manager import FirebaseManager


class AutomationOrchestrator:
    def __init__(self):
        self.data_dir = 'data'
        self.ensure_data_directory()

        print("🔧 Initializing automation system...\n")

        self.google_trends = GoogleTrendsScraper()
        self.content_gen = GeminiContentGenerator()
        self.uploader = GitHubUploader()
        self.poster = WhapiPoster()
        self.firebase = FirebaseManager()

        print("✅ All components initialized!\n")

    def ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def step_1_scrape_trends(self):
        print("=" * 60)
        print("STEP 1: SCRAPING TRENDING TOPICS")
        print("=" * 60 + "\n")

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
        print("=" * 60)
        print("STEP 2: GENERATING VIRAL CONTENT WITH GROQ AI")
        print("=" * 60 + "\n")

        print("🤖 Groq is analyzing trends and creating content...")

        content = self.content_gen.generate_viral_content(trends_summary)

        if not content:
            raise Exception("Failed to generate content")

        with open(f'{self.data_dir}/generated_content.json', 'w') as f:
            json.dump(content, f, indent=2)

        print("\n✅ Content generation complete!")
        print(f"\n📝 CAPTION PREVIEW:\n{content['viral_caption']}\n")
        print(f"🎨 PROMPT PREVIEW:\n{content['image_prompt'][:200]}...\n")

        return content

    def step_3_save_to_firebase(self, content):
        print("=" * 60)
        print("STEP 3: SAVING TO FIREBASE + KAGGLE INPUT")
        print("=" * 60 + "\n")

        # Save to Firebase
        post_id = self.firebase.save_post(content)
        if post_id:
            print(f"✅ Saved to Firebase with ID: {post_id}")
        else:
            print("⚠️  Firebase save failed — continuing without Firebase")
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Also save kaggle_input.json for Kaggle notebook
        kaggle_input = {
            'post_id': post_id,
            'positive_prompt': content['image_prompt'],
            'negative_prompt': content['negative_prompt'],
            'style': content['style'],
            'viral_caption': content['viral_caption'],
            'hashtags': content['hashtags'],
            'timestamp': datetime.now().isoformat()
        }

        with open(f'{self.data_dir}/kaggle_input.json', 'w') as f:
            json.dump(kaggle_input, f, indent=2)

        print(f"✅ Kaggle input saved: {self.data_dir}/kaggle_input.json\n")
        return post_id, 'output/generated_image.png'

    def step_4_upload_and_post(self, post_id, image_path, content):
        print("=" * 60)
        print("STEP 4: UPLOAD IMAGE + POST TO WHATSAPP")
        print("=" * 60 + "\n")

        if not os.path.exists(image_path):
            print(f"⚠️  Image not found at: {image_path}")
            print("   Run Kaggle notebook first to generate image!\n")
            return None

        # Upload to GitHub CDN
        print("📤 Uploading to GitHub CDN...")
        result = self.uploader.upload_image(image_path)

        if not result['success']:
            raise Exception(f"Upload failed: {result.get('error')}")

        image_url = result['url']
        print(f"✅ Uploaded! URL: {image_url}\n")

        # Update Firebase with image URL
        self.firebase.update_post_image(post_id, image_url)

        # Post to WhatsApp
        full_caption = f"{content['viral_caption']}\n\n{content['hashtags']}"
        print("📱 Posting to WhatsApp Channel...")
        post_result = self.poster.post_to_channel(image_url, full_caption)

        if post_result['success']:
            self.firebase.mark_posted(post_id)
            print(f"\n✅ Posted! Message ID: {post_result['message_id']}\n")
        else:
            print(f"❌ WhatsApp post failed: {post_result.get('error')}")

        return image_url

    def run_full_pipeline(self):
        print("\n" + "=" * 60)
        print("🚀 STARTING AI WHATSAPP AUTOMATION PIPELINE")
        print("=" * 60 + "\n")

        try:
            # Step 1 — Scrape trends
            trends_summary, _ = self.step_1_scrape_trends()

            # Step 2 — Generate content
            content = self.step_2_generate_content(trends_summary)

            # Step 3 — Save to Firebase + Kaggle input
            post_id, expected_image_path = self.step_3_save_to_firebase(content)

            print("⏸️  PIPELINE PAUSED — Waiting for Kaggle image generation")
            print(f"   Post ID: {post_id}")
            print(f"   Check Firebase Admin Panel to see the pending post\n")

            # Save state for continuation
            state = {
                'step': 'waiting_for_kaggle',
                'post_id': post_id,
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
        print("\n" + "=" * 60)
        print("▶️  CONTINUING PIPELINE — Post image + WhatsApp")
        print("=" * 60 + "\n")

        with open(f'{self.data_dir}/pipeline_state.json', 'r') as f:
            state = json.load(f)

        try:
            self.step_4_upload_and_post(
                state['post_id'],
                state['image_path'],
                state['content']
            )
            print("\n" + "=" * 60)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("=" * 60 + "\n")

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
