"""
Firebase Manager — Simple REST API with Database Secret
No JWT, no private key issues. Place at: scripts/firebase_manager.py
"""

import os
import requests
from datetime import datetime


class FirebaseManager:
    def __init__(self):
        self.database_url = os.getenv("FIREBASE_DATABASE_URL", "").rstrip("/")
        # Simple database secret — no JWT needed
        self.db_secret = os.getenv("FIREBASE_DB_SECRET", "")

        if not self.database_url:
            print("⚠️  FIREBASE_DATABASE_URL not set")
        if not self.db_secret:
            print("⚠️  FIREBASE_DB_SECRET not set")

    def _url(self, path):
        """Build Firebase REST URL with auth"""
        return f"{self.database_url}/{path}.json?auth={self.db_secret}"

    def _is_configured(self):
        return bool(self.database_url and self.db_secret)

    def save_post(self, content):
        """Save generated content to Firebase as a pending post"""
        if not self._is_configured():
            print("⚠️  Firebase not configured — skipping save")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        post_id = f"post_{timestamp}"

        post_data = {
            "post_id": post_id,
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
            "approved": True
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
                print(f"❌ Firebase save failed: {r.status_code} — {r.text}")
                return None
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            return None

    def update_post_image(self, post_id, image_url):
        """Update post with generated image URL"""
        if not self._is_configured():
            return False
        try:
            r = requests.patch(
                self._url(f"posts/{post_id}"),
                json={
                    "image_url": image_url,
                    "status": "ready_to_post"
                },
                timeout=15
            )
            if r.status_code == 200:
                print(f"✅ Image URL saved to Firebase")
                return True
            print(f"❌ Update failed: {r.text}")
        except Exception as e:
            print(f"❌ Firebase update error: {e}")
        return False

    def mark_posted(self, post_id):
        """Mark post as successfully posted to WhatsApp"""
        if not self._is_configured():
            return False
        try:
            r = requests.patch(
                self._url(f"posts/{post_id}"),
                json={
                    "status": "posted",
                    "posted_at": datetime.now().isoformat()
                },
                timeout=15
            )
            return r.status_code == 200
        except Exception:
            return False

    def get_pending_posts(self):
        """Get posts waiting for image generation"""
        if not self._is_configured():
            return {}
        try:
            r = requests.get(self._url("posts"), timeout=15)
            if r.status_code == 200:
                posts = r.json() or {}
                return {
                    pid: p for pid, p in posts.items()
                    if isinstance(p, dict)
                    and p.get("status") == "pending_image"
                }
        except Exception as e:
            print(f"❌ Firebase fetch error: {e}")
        return {}

    def get_ready_posts(self):
        """Get posts ready to post to WhatsApp"""
        if not self._is_configured():
            return {}
        try:
            r = requests.get(self._url("posts"), timeout=15)
            if r.status_code == 200:
                posts = r.json() or {}
                return {
                    pid: p for pid, p in posts.items()
                    if isinstance(p, dict)
                    and p.get("status") == "ready_to_post"
                    and p.get("approved", True)
                }
        except Exception as e:
            print(f"❌ Firebase fetch error: {e}")
        return {}

    def get_settings(self):
        """Get automation settings"""
        if not self._is_configured():
            return {"auto_post": True, "require_approval": False}
        try:
            r = requests.get(self._url("settings"), timeout=15)
            if r.status_code == 200:
                return r.json() or {}
        except Exception:
            pass
        return {"auto_post": True, "require_approval": False}
