"""
Reference Image Analyzer
Analyzes the reference face and extracts key characteristics
This ensures the AI maintains facial consistency in generated images
"""

from PIL import Image
import json


class ReferenceAnalyzer:
    """
    Analyzes reference image and creates structured prompt components
    """
    
    def __init__(self, reference_image_path):
        self.reference_path = reference_image_path
        self.characteristics = self.analyze_reference()
    
    def analyze_reference(self):
        """
        This would ideally use face analysis, but for simplicity,
        we'll create a template that you fill in manually once
        
        YOU MUST UPDATE THIS BASED ON YOUR REFERENCE IMAGE
        """
        
        # IMPORTANT: Update these characteristics based on YOUR reference person
        characteristics = {
            "age": "18-22 years old",
            "gender": "male",
            "ethnicity": "South Asian",
            "skin_tone": "warm brown skin tone",
            
            # Facial Features
            "face_shape": "sharp jawline with defined cheekbones",
            "eyes": "brown eyes, naturally expressive",
            "nose": "proportionate nose",
            "lips": "natural lips",
            
            # Hair
            "hairstyle": "medium-length black textured hair",
            "hair_description": "natural wavy black hair with volume",
            
            # Facial Hair
            "facial_hair": "thin mustache",
            "beard": "clean shaven with thin mustache only",
            
            # Additional Features
            "accessories": "none",  # Update if glasses, earrings, etc.
            "build": "lean athletic build",
            
            # Style Preferences
            "fashion": "modern casual streetwear, hoodies, minimalist aesthetic",
            
            # Distinctive Features
            "distinctive": "youthful appearance, confident expression"
        }
        
        return characteristics
    
    def get_base_character_prompt(self):
        """
        Generate the base character description for all prompts
        This ensures consistency across all generated images
        """
        c = self.characteristics
        
        prompt = f"""A realistic {c['age']} {c['ethnicity']} {c['gender']} with {c['hairstyle']}, {c['facial_hair']}, {c['face_shape']}, {c['skin_tone']}, {c['eyes']}"""
        
        return prompt.strip()
    
    def get_detailed_prompt_components(self):
        """
        Get all components for building prompts
        """
        return {
            "age": self.characteristics["age"],
            "ethnicity": self.characteristics["ethnicity"],
            "gender": self.characteristics["gender"],
            "hairstyle": self.characteristics["hairstyle"],
            "facial_hair": self.characteristics["facial_hair"],
            "face_details": f"{self.characteristics['face_shape']}, {self.characteristics['skin_tone']}, {self.characteristics['eyes']}",
            "build": self.characteristics["build"],
            "fashion_base": self.characteristics["fashion"]
        }
    
    def save_characteristics(self, output_path='config/reference_characteristics.json'):
        """
        Save characteristics to JSON for reference
        """
        with open(output_path, 'w') as f:
            json.dump(self.characteristics, f, indent=2)
        
        print(f"✅ Reference characteristics saved to {output_path}")


def main():
    """
    Test and save reference characteristics
    """
    analyzer = ReferenceAnalyzer('assets/reference_face.png')
    
    print("Base Character Prompt:")
    print(analyzer.get_base_character_prompt())
    print("\n" + "="*50 + "\n")
    
    print("Detailed Components:")
    components = analyzer.get_detailed_prompt_components()
    for key, value in components.items():
        print(f"{key}: {value}")
    
    # Save to file
    analyzer.save_characteristics()


if __name__ == "__main__":
    main()
