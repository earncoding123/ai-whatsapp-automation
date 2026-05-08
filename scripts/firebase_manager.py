"""
Firebase Manager
Handles all Firebase Realtime Database operations
"""

import json
import os
import requests
from datetime import datetime


class FirebaseManager:
    def __init__(self):
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "")
        self.database_url = os.getenv("FIREBASE_DATABASE_URL", "")
        self.api_key = os.getenv("FIREBASE_API_KEY", "")
        # For server-side auth we use a simple secret
        self.db_secret = os.getenv("FIREBASE_DB_SECRET", "")

    def _url(self, path):
        return f"{self.database_url}/{path}.json?auth={self.db_secret}"

    def save_post(self, content):
        """Save generated content to Firebase as a pending post"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        post_id = f"post_{timestamp}"

        post_data = {
            "status": "pending_image",
            "trend_title": content.get("trend_title", ""),
            "viral_caption": content.get("viral_caption", ""),
            "image_prompt": content.get("image_prompt", ""),
            "negative_prompt": content.get("negative_prompt", ""),
            "style": content.get("style", ""),
            "hashtags": content.get("hashtags", ""),
            "created_at": datetime.now().isoformat(),
            "image_url": None,
            "posted_at": None,
            "approved": True,
            "post_id": post_id
        }

        try:
            r = requests.put(
                self._url(f"posts/{post_id}"),
                json=post_data,
                timeout=15
            )
            if r.status_code == 200:
                print(f"✅ Post saved to Firebase: {post_id}")
                return post_id
            else:
                print(f"❌ Firebase save failed: {r.text}")
                return None
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            return None

    def update_post_image(self, post_id, image_url):
        """Update post with generated image URL"""
        try:
            r = requests.patch(
                self._url(f"posts/{post_id}"),
                json={"image_url": image_url, "status": "ready_to_post"},
                timeout=15
            )
            if r.status_code == 200:
                print(f"✅ Image URL saved to Firebase")
                return True
        except Exception as e:
            print(f"❌ Firebase update error: {e}")
        return False

    def mark_posted(self, post_id):
        """Mark post as successfully posted to WhatsApp"""
        try:
            r = requests.patch(
                self._url(f"posts/{post_id}"),
                json={"status": "posted", "posted_at": datetime.now().isoformat()},
                timeout=15
            )
            return r.status_code == 200
        except:
            return False

    def get_pending_posts(self):
        """Get posts waiting for image generation"""
        try:
            r = requests.get(self._url("posts"), timeout=15)
            if r.status_code == 200:
                posts = r.json() or {}
                return {
                    pid: p for pid, p in posts.items()
                    if p.get("status") == "pending_image"
                }
        except Exception as e:
            print(f"❌ Firebase fetch error: {e}")
        return {}

    def get_ready_posts(self):
        """Get posts ready to be posted to WhatsApp"""
        try:
            r = requests.get(self._url("posts"), timeout=15)
            if r.status_code == 200:
                posts = r.json() or {}
                return {
                    pid: p for pid, p in posts.items()
                    if p.get("status") == "ready_to_post" and p.get("approved", True)
                }
        except Exception as e:
            print(f"❌ Firebase fetch error: {e}")
        return {}

    def get_settings(self):
        """Get automation settings"""
        try:
            r = requests.get(self._url("settings"), timeout=15)
            if r.status_code == 200:
                return r.json() or {}
        except:
            pass
        return {"auto_post": True, "require_approval": False}

    def save_settings(self, settings):
        """Save automation settings"""
        try:
            r = requests.put(self._url("settings"), json=settings, timeout=15)
            return r.status_code == 200
        except:
            return False
