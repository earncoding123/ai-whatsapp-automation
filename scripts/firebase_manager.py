"""
Firebase Manager — uses Admin SDK (service account)
Place this file at: scripts/firebase_manager.py
"""

import json
import os
import requests
from datetime import datetime


class FirebaseManager:
    def __init__(self):
    self.project_id = os.getenv("FIREBASE_PROJECT_ID", "")
    self.database_url = os.getenv("FIREBASE_DATABASE_URL", "").rstrip("/")
    self.client_email = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    
    # Fix \n in private key — handles both formats
    raw_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
    # If stored as literal \n replace with actual newlines
    if "\\n" in raw_key:
        self.private_key = raw_key.replace("\\n", "\n")
    else:
        self.private_key = raw_key
    
    self._token = None
    self._token_expiry = 0

    def _get_access_token(self):
        """Get OAuth2 access token from service account"""
        import time, jwt  # pip install PyJWT

        now = int(time.time())
        if self._token and now < self._token_expiry - 60:
            return self._token

        payload = {
            "iss": self.client_email,
            "sub": self.client_email,
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
            "scope": "https://www.googleapis.com/auth/firebase.database https://www.googleapis.com/auth/userinfo.email"
        }

        signed = jwt.encode(payload, self.private_key, algorithm="RS256")

        r = requests.post("https://oauth2.googleapis.com/token", data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signed
        }, timeout=15)

        if r.status_code == 200:
            data = r.json()
            self._token = data["access_token"]
            self._token_expiry = now + data.get("expires_in", 3600)
            return self._token
        else:
            print(f"❌ Token error: {r.text}")
            return None

    def _url(self, path):
        return f"{self.database_url}/{path}.json"

    def _headers(self):
        token = self._get_access_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def save_post(self, content):
        """Save generated content to Firebase as a pending post"""
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
                headers=self._headers(),
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
        """Update post with generated image URL — call from Kaggle"""
        try:
            r = requests.patch(
                self._url(f"posts/{post_id}"),
                headers=self._headers(),
                json={"image_url": image_url, "status": "ready_to_post"},
                timeout=15
            )
            if r.status_code == 200:
                print(f"✅ Image URL saved to Firebase for {post_id}")
                return True
            print(f"❌ Update failed: {r.text}")
        except Exception as e:
            print(f"❌ Firebase update error: {e}")
        return False

    def mark_posted(self, post_id):
        """Mark post as successfully posted to WhatsApp"""
        try:
            r = requests.patch(
                self._url(f"posts/{post_id}"),
                headers=self._headers(),
                json={"status": "posted", "posted_at": datetime.now().isoformat()},
                timeout=15
            )
            return r.status_code == 200
        except:
            return False

    def get_pending_posts(self):
        """Get posts waiting for image generation (for Kaggle to pick up)"""
        try:
            r = requests.get(self._url("posts"), headers=self._headers(), timeout=15)
            if r.status_code == 200:
                posts = r.json() or {}
                return {
                    pid: p for pid, p in posts.items()
                    if isinstance(p, dict) and p.get("status") == "pending_image"
                }
        except Exception as e:
            print(f"❌ Firebase fetch error: {e}")
        return {}

    def get_ready_posts(self):
        """Get posts ready to be posted to WhatsApp"""
        try:
            r = requests.get(self._url("posts"), headers=self._headers(), timeout=15)
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
        """Get automation settings from Firebase"""
        try:
            r = requests.get(self._url("settings"), headers=self._headers(), timeout=15)
            if r.status_code == 200:
                return r.json() or {}
        except:
            pass
        return {"auto_post": True, "require_approval": False}
