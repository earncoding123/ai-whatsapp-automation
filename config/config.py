"""
Configuration file for AI WhatsApp Channel Automation
Store your API keys and settings here
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==============================================
# API CREDENTIALS
# ==============================================

# Gemini AI
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Whapi WhatsApp API
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "")
WHAPI_CHANNEL_ID = os.getenv("WHAPI_CHANNEL_ID", "")  # Your WhatsApp Channel ID

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# Reddit API
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "AI-WhatsApp-Bot/1.0")

# Kaggle API (for triggering notebook)
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")
KAGGLE_NOTEBOOK_URL = os.getenv("KAGGLE_NOTEBOOK_URL", "")  # Your Kaggle notebook kernel URL

# ==============================================
# SYSTEM SETTINGS
# ==============================================

# Reference Image
REFERENCE_IMAGE_PATH = "assets/reference_face.png"

# Trend Sources
REDDIT_SUBREDDITS = [
    "artificial",
    "singularity", 
    "ChatGPT",
    "technology",
    "Futurology",
    "AIart"
]

# Visual Styles (randomly selected daily)
VISUAL_STYLES = [
    "cinematic portrait",
    "hyper realistic photography",
    "neo noir aesthetic",
    "futuristic tech influencer",
    "luxury dark mode portrait",
    "motivational poster style",
    "AI god mode aesthetic",
    "professional headshot style",
    "dramatic lighting portrait",
    "viral instagram aesthetic"
]

# ComfyUI Settings
COMFYUI_SETTINGS = {
    "ip_adapter_weight": 0.8,
    "denoise": 0.5,
    "cfg": 7.0,
    "steps": 30,
    "sampler": "DPM++ 2M Karras",
    "scheduler": "karras"
}

# Image Generation Settings
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024
SEED = -1  # -1 for random, or set fixed number for consistency

# Posting Schedule
POST_TIME_UTC = "08:00"  # 8 AM UTC daily
