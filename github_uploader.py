"""
GitHub CDN Image Uploader
Uploads generated images to GitHub repo and returns a public CDN URL.
No Cloudinary account needed - completely free!
"""

import requests
import base64
import os
from datetime import datetime


class GitHubUploader:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")          # GitHub Personal Access Token
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "") # Your GitHub username
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "ai-whatsapp-automation")
        self.branch = "main"
        self.upload_folder = "generated_images"

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

    def upload_image(self, image_path):
        """
        Upload image to GitHub repo and return raw CDN URL.

        Args:
            image_path: Local path to the image file

        Returns:
            dict: { success, url, path }
        """
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"post_{timestamp}.jpg"
            file_path = f"{self.upload_folder}/{filename}"

            # GitHub API endpoint
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"

            payload = {
                "message": f"Auto-upload: {filename}",
                "content": image_data,
                "branch": self.branch
            }

            response = requests.put(api_url, headers=self.headers, json=payload, timeout=60)

            if response.status_code in (200, 201):
                # Build raw CDN URL
                cdn_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/{self.branch}/{file_path}"
                print(f"✅ Image uploaded to GitHub!")
                print(f"🔗 CDN URL: {cdn_url}")
                return {
                    "success": True,
                    "url": cdn_url,
                    "path": file_path
                }
            else:
                print(f"❌ Upload failed: {response.status_code} — {response.text}")
                return {"success": False, "error": response.text}

        except FileNotFoundError:
            print(f"❌ Image file not found: {image_path}")
            return {"success": False, "error": "File not found"}
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return {"success": False, "error": str(e)}


def main():
    uploader = GitHubUploader()
    result = uploader.upload_image("assets/reference_face.png")
    if result["success"]:
        print(f"\n✅ Test upload successful!")
        print(f"URL: {result['url']}")
    else:
        print(f"\n❌ Test upload failed: {result['error']}")


if __name__ == "__main__":
    main()
