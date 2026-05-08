"""
Whapi WhatsApp Channel Poster
Posts content to WhatsApp Channel using Whapi API
"""

import requests
import json
from config.config import WHAPI_TOKEN, WHAPI_CHANNEL_ID


class WhapiPoster:
    def __init__(self):
        self.token = WHAPI_TOKEN
        self.channel_id = WHAPI_CHANNEL_ID
        self.base_url = "https://gate.whapi.cloud"
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def post_to_channel(self, image_url, caption):
        """
        Post image with caption to WhatsApp Channel
        
        Args:
            image_url: Public URL of the image
            caption: Text caption for the post
            
        Returns:
            dict: Response from Whapi API
        """
        
        endpoint = f"{self.base_url}/messages/image"
        
        payload = {
            "to": self.channel_id,
            "media": image_url,
            "caption": caption
        }
        
        try:
            print("📤 Posting to WhatsApp Channel...")
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                print("✅ Successfully posted to WhatsApp Channel!")
                return {
                    'success': True,
                    'message_id': result.get('id', 'unknown'),
                    'response': result
                }
            else:
                print(f"❌ Failed to post. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return {
                'success': False,
                'error': 'Request timeout'
            }
        except Exception as e:
            print(f"❌ Error posting to channel: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_text_only(self, text):
        """
        Post text-only message to channel
        """
        endpoint = f"{self.base_url}/messages/text"
        
        payload = {
            "to": self.channel_id,
            "body": text
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                print("✅ Text message posted successfully!")
                return {'success': True, 'response': response.json()}
            else:
                print(f"❌ Failed to post text. Status: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"❌ Error posting text: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_channel_status(self):
        """
        Check if channel is accessible
        """
        endpoint = f"{self.base_url}/channels/{self.channel_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Channel is accessible")
                return {'success': True, 'data': response.json()}
            else:
                print(f"⚠️ Channel check failed: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"❌ Error checking channel: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """
    Test the Whapi poster
    """
    poster = WhapiPoster()
    
    # Test 1: Check channel
    print("Testing channel access...\n")
    status = poster.check_channel_status()
    
    # Test 2: Post sample content
    test_image_url = "https://via.placeholder.com/1024x1024.jpg"
    test_caption = """🚀 The Future is Here!

AI technology is transforming how we create and share content. This is a test post from our automated AI channel.

#AI #Technology #Future #Innovation"""
    
    print("\nTesting image post...\n")
    result = poster.post_to_channel(test_image_url, test_caption)
    
    if result['success']:
        print(f"\n✅ Test post successful!")
        print(f"Message ID: {result['message_id']}")
    else:
        print(f"\n❌ Test post failed!")


if __name__ == "__main__":
    main()
