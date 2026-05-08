"""
Cloudinary Image Uploader
Uploads generated images to Cloudinary and returns public URL
"""

import cloudinary
import cloudinary.uploader
from config.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET
)
from datetime import datetime


class CloudinaryUploader:
    def __init__(self):
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )
    
    def upload_image(self, image_path, folder="ai-whatsapp-channel"):
        """
        Upload image to Cloudinary and return public URL
        
        Args:
            image_path: Local path to the image
            folder: Cloudinary folder name
            
        Returns:
            dict: Upload result with URL
        """
        try:
            # Generate unique public_id with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            public_id = f"{folder}/post_{timestamp}"
            
            # Upload image
            result = cloudinary.uploader.upload(
                image_path,
                public_id=public_id,
                folder=folder,
                overwrite=True,
                resource_type="image",
                quality="auto:best",
                format="jpg"
            )
            
            print(f"✅ Image uploaded successfully!")
            print(f"📎 URL: {result['secure_url']}")
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result['width'],
                'height': result['height'],
                'format': result['format'],
                'size': result['bytes']
            }
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_image_url(self, public_id):
        """
        Get URL for an existing image
        """
        return cloudinary.CloudinaryImage(public_id).build_url()


def main():
    """
    Test uploader
    """
    uploader = CloudinaryUploader()
    
    # Test with a sample image (you'll replace this)
    test_image = "assets/reference_face.png"
    
    print("Uploading test image...")
    result = uploader.upload_image(test_image)
    
    if result['success']:
        print(f"\n✅ Test upload successful!")
        print(f"Image URL: {result['url']}")
    else:
        print(f"\n❌ Test upload failed: {result['error']}")


if __name__ == "__main__":
    main()
