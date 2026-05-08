"""
MAIN ORCHESTRATOR
This script runs the entire automation pipeline
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.trends.reddit_scraper import RedditScraper
from scripts.trends.google_trends_scraper import GoogleTrendsScraper
from scripts.ai.gemini_generator import GeminiContentGenerator
from scripts.upload.cloudinary_uploader import CloudinaryUploader
from scripts.whatsapp.whapi_poster import WhapiPoster


class AutomationOrchestrator:
    def __init__(self):
        self.data_dir = 'data'
        self.ensure_data_directory()
        
        # Initialize all components
        print("🔧 Initializing automation system...\n")
        
        self.reddit = RedditScraper()
        self.google_trends = GoogleTrendsScraper()
        self.content_gen = GeminiContentGenerator()
        self.uploader = CloudinaryUploader()
        self.poster = WhapiPoster()
        
        print("✅ All components initialized!\n")
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def step_1_scrape_trends(self):
        """
        STEP 1: Scrape trending topics from Reddit and Google
        """
        print("="*60)
        print("STEP 1: SCRAPING TRENDING TOPICS")
        print("="*60 + "\n")
        
        # Scrape Reddit
        print("📡 Scraping Reddit...")
        reddit_summary, reddit_data = self.reddit.get_trending_summary()
        
        # Scrape Google Trends
        print("📡 Scraping Google Trends...")
        google_summary, google_data = self.google_trends.get_comprehensive_trends()
        
        # Combine summaries
        combined_summary = f"{reddit_summary}\n\n{google_summary}"
        
        # Save data
        trends_data = {
            'reddit': reddit_data,
            'google': google_data,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f'{self.data_dir}/trends_data.json', 'w') as f:
            json.dump(trends_data, f, indent=2)
        
        print("\n✅ Trend scraping complete!\n")
        
        return combined_summary, trends_data
    
    def step_2_generate_content(self, trends_summary):
        """
        STEP 2: Generate viral content using Gemini AI
        """
        print("="*60)
        print("STEP 2: GENERATING VIRAL CONTENT WITH GEMINI AI")
        print("="*60 + "\n")
        
        print("🤖 Gemini is analyzing trends and creating content...")
        
        content = self.content_gen.generate_viral_content(trends_summary)
        
        if not content:
            raise Exception("Failed to generate content with Gemini")
        
        # Save generated content
        with open(f'{self.data_dir}/generated_content.json', 'w') as f:
            json.dump(content, f, indent=2)
        
        print("\n✅ Content generation complete!")
        print(f"\n📝 CAPTION PREVIEW:\n{content['viral_caption']}\n")
        print(f"🎨 PROMPT PREVIEW:\n{content['image_prompt'][:200]}...\n")
        
        return content
    
    def step_3_send_to_kaggle(self, content):
        """
        STEP 3: Send prompt to Kaggle for image generation
        
        NOTE: This requires manual setup in Kaggle notebook
        For now, we'll save the prompt for Kaggle to pick up
        """
        print("="*60)
        print("STEP 3: PREPARING FOR KAGGLE IMAGE GENERATION")
        print("="*60 + "\n")
        
        # Create Kaggle input file
        kaggle_input = {
            'positive_prompt': content['image_prompt'],
            'negative_prompt': content['negative_prompt'],
            'style': content['style'],
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f'{self.data_dir}/kaggle_input.json', 'w') as f:
            json.dump(kaggle_input, f, indent=2)
        
        print("✅ Kaggle input file created!")
        print(f"📁 Location: {self.data_dir}/kaggle_input.json")
        print("\n⚠️  MANUAL STEP REQUIRED:")
        print("   1. Your Kaggle notebook should read this file")
        print("   2. Run ComfyUI with the prompt")
        print("   3. Save generated image to: output/generated_image.png")
        print("   4. The workflow will automatically continue\n")
        
        # For automation, we'll assume Kaggle generates: output/generated_image.png
        # In production, you'd trigger Kaggle API or use polling
        
        return 'output/generated_image.png'  # Expected output path
    
    def step_4_upload_image(self, image_path):
        """
        STEP 4: Upload generated image to Cloudinary
        """
        print("="*60)
        print("STEP 4: UPLOADING IMAGE TO CLOUDINARY")
        print("="*60 + "\n")
        
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"⚠️  Waiting for image at: {image_path}")
            print("   Make sure Kaggle has generated the image!\n")
            return None
        
        print("📤 Uploading to Cloudinary...")
        
        result = self.uploader.upload_image(image_path)
        
        if not result['success']:
            raise Exception(f"Upload failed: {result.get('error')}")
        
        print(f"\n✅ Image uploaded successfully!")
        print(f"🔗 URL: {result['url']}\n")
        
        return result['url']
    
    def step_5_post_to_whatsapp(self, image_url, content):
        """
        STEP 5: Post to WhatsApp Channel
        """
        print("="*60)
        print("STEP 5: POSTING TO WHATSAPP CHANNEL")
        print("="*60 + "\n")
        
        # Combine caption with hashtags
        full_caption = f"{content['viral_caption']}\n\n{content['hashtags']}"
        
        print("📱 Posting to WhatsApp Channel...")
        
        result = self.poster.post_to_channel(image_url, full_caption)
        
        if not result['success']:
            raise Exception(f"Posting failed: {result.get('error')}")
        
        print(f"\n✅ Successfully posted to WhatsApp Channel!")
        print(f"📨 Message ID: {result['message_id']}\n")
        
        return result
    
    def run_full_pipeline(self):
        """
        Run the complete automation pipeline
        """
        print("\n" + "="*60)
        print("🚀 STARTING AI WHATSAPP AUTOMATION PIPELINE")
        print("="*60 + "\n")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Scrape trends
            trends_summary, trends_data = self.step_1_scrape_trends()
            
            # Step 2: Generate content
            content = self.step_2_generate_content(trends_summary)
            
            # Step 3: Prepare for Kaggle
            expected_image_path = self.step_3_send_to_kaggle(content)
            
            print("⏸️  PIPELINE PAUSED - Waiting for Kaggle")
            print("   After Kaggle generates the image, run:")
            print("   python scripts/main.py --continue\n")
            
            # Save state for continuation
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
        """
        Continue pipeline after Kaggle generates image
        """
        print("\n" + "="*60)
        print("▶️  CONTINUING AI WHATSAPP AUTOMATION PIPELINE")
        print("="*60 + "\n")
        
        # Load state
        with open(f'{self.data_dir}/pipeline_state.json', 'r') as f:
            state = json.load(f)
        
        try:
            # Step 4: Upload image
            image_url = self.step_4_upload_image(state['image_path'])
            
            if not image_url:
                print("❌ Image not found. Make sure Kaggle generated it!")
                return
            
            # Step 5: Post to WhatsApp
            result = self.step_5_post_to_whatsapp(image_url, state['content'])
            
            print("\n" + "="*60)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*60 + "\n")
            
            # Save completion log
            completion_log = {
                'completed_at': datetime.now().isoformat(),
                'content': state['content'],
                'image_url': image_url,
                'whatsapp_result': result
            }
            
            with open(f'{self.data_dir}/completion_log.json', 'w') as f:
                json.dump(completion_log, f, indent=2)
            
        except Exception as e:
            print(f"\n❌ CONTINUATION FAILED: {e}")
            import traceback
            traceback.print_exc()


def main():
    """
    Main entry point
    """
    orchestrator = AutomationOrchestrator()
    
    # Check if continuing from Kaggle
    if len(sys.argv) > 1 and sys.argv[1] == '--continue':
        orchestrator.continue_pipeline()
    else:
        orchestrator.run_full_pipeline()


if __name__ == "__main__":
    main()
