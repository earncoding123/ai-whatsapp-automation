"""
Gemini AI Content Generator
The BRAIN of the automation system
Analyzes trends and generates viral WhatsApp content
"""

import google.generativeai as genai
import json
import random
from datetime import datetime
from config.config import GEMINI_API_KEY, VISUAL_STYLES
from scripts.ai.reference_analyzer import ReferenceAnalyzer


class GeminiContentGenerator:
    def __init__(self, reference_image_path='assets/reference_face.png'):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load reference characteristics
        self.ref_analyzer = ReferenceAnalyzer(reference_image_path)
        self.base_character = self.ref_analyzer.get_base_character_prompt()
        self.character_components = self.ref_analyzer.get_detailed_prompt_components()
    
    def create_system_prompt(self):
        """
        The MASTER prompt that guides Gemini's content creation
        """
        
        system_prompt = f"""You are a VIRAL VISUAL CONTENT STRATEGIST for a WhatsApp AI channel.

Your mission: Create highly engaging, shareable AI-generated content that feels REAL, CINEMATIC, and EMOTIONALLY POWERFUL.

## REFERENCE CHARACTER (MUST MAINTAIN IN EVERY IMAGE):
{json.dumps(self.character_components, indent=2)}

## BASE CHARACTER DESCRIPTION (USE IN ALL PROMPTS):
{self.base_character}

## YOUR TASK:
1. Analyze the provided trending topics
2. Select the MOST VIRAL-WORTHY topic
3. Create a captivating visual concept that combines:
   - The trending topic
   - The reference character in a relevant scenario
   - A cinematic aesthetic
   - Emotional impact

## CRITICAL REQUIREMENTS:

### Character Consistency:
- ALWAYS include the base character description
- MAINTAIN: age, hairstyle, facial hair, ethnicity, face shape, skin tone
- The character should be DOING something related to the trend
- Natural, realistic portrayal

### Visual Quality:
- Ultra realistic photography style
- Cinematic lighting and composition
- Professional color grading
- Viral social media aesthetic
- 8K quality, masterpiece level

### Prompt Structure:
Your image_prompt MUST follow this structure:

[BASE CHARACTER DESCRIPTION], [ACTION/SCENARIO RELATED TO TREND], [VISUAL STYLE], [TECHNICAL QUALITY KEYWORDS]

Example:
"A realistic 18-year-old South Asian male with medium black textured hair, thin mustache, sharp jawline, warm brown skin tone, sitting in a futuristic AI command center with holographic displays, cinematic portrait, ultra realistic photography, dramatic blue and orange lighting, depth of field, highly detailed skin texture, professional color grading, viral instagram aesthetic, 8k, masterpiece"

### Caption Requirements:
- Hook in first line
- Include the trend context
- Motivational or thought-provoking
- 2-4 sentences
- Include relevant emojis
- Feel human, not robotic

### Hashtags:
- 5-8 hashtags
- Mix of trending and niche
- Include: #AI #Technology #Future

## OUTPUT FORMAT (STRICT JSON):

{{
  "trend_title": "The specific trend you're addressing",
  "viral_caption": "The WhatsApp caption with emojis",
  "image_prompt": "Complete SDXL prompt with base character + scenario",
  "negative_prompt": "blurry face, deformed eyes, extra fingers, low quality, duplicate face, distorted hair, unrealistic skin, cartoon, bad anatomy, mutated hands, cropped face, ugly teeth, unrealistic beard, asymmetrical eyes, multiple people, crowd, text, watermark",
  "style": "The visual style used",
  "hashtags": "#AI #Technology #Future #etc",
  "reasoning": "Why this trend + visual combo will be viral"
}}

## EXAMPLES OF GOOD SCENARIOS:

Trend: "AI replacing jobs"
Scenario: Character working alongside holographic AI assistant in modern office

Trend: "GPT-5 breakthrough"
Scenario: Character in cyberpunk setting with neural interface, matrix-style

Trend: "Future of education"
Scenario: Character in futuristic library with floating holographic books

IMPORTANT: The character should ALWAYS be the main subject, placed in scenarios that visualize the trend.

Return ONLY valid JSON. No markdown, no explanation, just JSON.
"""
        
        return system_prompt
    
    def generate_viral_content(self, trends_summary):
        """
        Generate viral content based on trending topics
        """
        
        # Select random visual style
        selected_style = random.choice(VISUAL_STYLES)
        
        # Create the prompt
        user_prompt = f"""## TRENDING TOPICS TODAY:

{trends_summary}

## SELECTED VISUAL STYLE:
{selected_style}

## YOUR TASK:
Analyze these trends and create ONE highly viral WhatsApp post that:
1. Addresses the most engaging trend
2. Features the reference character in a relevant cinematic scenario
3. Uses the selected visual style: {selected_style}
4. Feels authentic and shareable

Generate the JSON response now.
"""
        
        try:
            # Call Gemini
            response = self.model.generate_content(
                [self.create_system_prompt(), user_prompt]
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            content = json.loads(response_text)
            
            # Add metadata
            content['generated_at'] = datetime.now().isoformat()
            content['base_character'] = self.base_character
            
            return content
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {response.text}")
            return None
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return None
    
    def enhance_prompt_with_quality_keywords(self, base_prompt):
        """
        Add quality enhancement keywords to the prompt
        """
        quality_keywords = """
ultra realistic photography,
highly detailed skin texture,
natural facial features,
realistic hair texture,
sharp focus on face,
professional lighting,
cinematic color grading,
depth of field,
8k resolution,
masterpiece quality,
photorealistic,
high detail,
trending on social media,
viral aesthetic
"""
        
        return f"{base_prompt}, {quality_keywords}"


def main():
    """
    Test the Gemini content generator
    """
    
    # Sample trending topics
    sample_trends = """
## TRENDING AI/TECH TOPICS TODAY

1. **GPT-5 Rumors: OpenAI's Next Big Release**
   - Subreddit: r/artificial
   - Engagement: 5,432 upvotes, 892 comments

2. **AI Voice Cloning Reaches Human-Level Quality**
   - Subreddit: r/singularity
   - Engagement: 3,211 upvotes, 445 comments

3. **Meta Releases Open-Source AI Model**
   - Subreddit: r/technology
   - Engagement: 4,556 upvotes, 621 comments
"""
    
    generator = GeminiContentGenerator()
    
    print("Generating viral content...\n")
    
    content = generator.generate_viral_content(sample_trends)
    
    if content:
        print("✅ GENERATED CONTENT:\n")
        print(json.dumps(content, indent=2))
        
        # Save to file
        with open('data/generated_content.json', 'w') as f:
            json.dump(content, f, indent=2)
        
        print("\n✅ Content saved to data/generated_content.json")
    else:
        print("❌ Failed to generate content")


if __name__ == "__main__":
    main()
