"""
Content Generation Module
Generates social media posts (text + images) based on agent decisions
"""

import os
import requests
from PIL import Image
from io import BytesIO
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Optional
import time

load_dotenv()


class ContentGenerator:
    """Generate social media content (text and images)"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # Image generation API
        self.image_api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    def generate_post_text(self, decision: Dict, context: Dict, platform: str = "twitter") -> Dict:
        """Generate final post text based on arbitrator's decision"""
        
        platform_specs = {
            "twitter": {
                "char_limit": 280,
                "style": "Punchy, concise, engaging. Use 1-2 relevant hashtags. Make it quotable.",
                "hashtag_count": 2
            },
            "instagram": {
                "char_limit": 2200,
                "style": "Visual storytelling, conversational, emoji-friendly. Use 5-10 hashtags.",
                "hashtag_count": 8
            },
            "linkedin": {
                "char_limit": 3000,
                "style": "Professional, value-driven, thought leadership. Use 3-5 hashtags.",
                "hashtag_count": 4
            }
        }
        
        spec = platform_specs.get(platform.lower(), platform_specs["twitter"])
        
        prompt = f"""Generate a {platform.upper()} post based on this marketing decision:

BRAND: {context.get('brand_name', 'Tech Startup')}
PRODUCT: {context.get('product_info', 'AI Product')}
TARGET AUDIENCE: {context.get('target_audience', 'Tech professionals')}

DECISION FROM COUNCIL:
{decision.get('decision', 'Create engaging post')}

IMPLEMENTATION STRATEGY:
{decision.get('implementation', 'Professional approach')}

PLATFORM: {platform.upper()}
CHARACTER LIMIT: {spec['char_limit']}
STYLE GUIDE: {spec['style']}

Generate a complete post that:
1. Captures attention immediately
2. Communicates the key value proposition
3. Includes {spec['hashtag_count']} relevant hashtags
4. Stays under {spec['char_limit']} characters
5. Includes a clear call-to-action

Provide ONLY the post text, ready to publish. No explanations or meta-commentary.
"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert social media copywriter. Write compelling, platform-optimized posts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            post_text = response.choices[0].message.content.strip()
            
            # Extract hashtags
            hashtags = [word for word in post_text.split() if word.startswith('#')]
            
            # Determine posting time (mock logic)
            posting_times = {
                "twitter": "9:00 AM EST",
                "instagram": "11:00 AM EST",
                "linkedin": "8:00 AM EST"
            }
            
            return {
                "platform": platform,
                "caption": post_text,
                "hashtags": hashtags,
                "posting_time": posting_times.get(platform, "9:00 AM EST"),
                "char_count": len(post_text)
            }
            
        except Exception as e:
            return {
                "platform": platform,
                "caption": f"Error generating post: {str(e)}",
                "hashtags": [],
                "posting_time": "N/A",
                "char_count": 0
            }
    
    def generate_image(self, prompt: str, filename: str = "generated_post.png", 
                      max_retries: int = 3) -> Optional[str]:
        """Generate image using HuggingFace Stable Diffusion"""
        
        if not self.hf_token:
            print("⚠️ HuggingFace token not found - skipping image generation")
            return None
        
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        # Enhance prompt for better results
        enhanced_prompt = f"{prompt}, professional marketing image, high quality, clean design, product photography style, 4k"
        
        for attempt in range(max_retries):
            try:
                print(f"🎨 Generating image (attempt {attempt + 1}/{max_retries})...")
                
                response = requests.post(
                    self.image_api_url,
                    headers=headers,
                    json={"inputs": enhanced_prompt},
                    timeout=60
                )
                
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    
                    # Save image
                    output_path = f"outputs/generated_images/{filename}"
                    os.makedirs("outputs/generated_images", exist_ok=True)
                    image.save(output_path)
                    
                    print(f"✅ Image saved: {output_path}")
                    return output_path
                
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    print(f"⏳ Model loading, waiting 20 seconds...")
                    time.sleep(20)
                    continue
                
                else:
                    print(f"❌ Image generation failed: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(10)
        
        print("⚠️ Image generation failed after all retries")
        return None
    
    def create_image_prompt(self, decision: Dict, context: Dict) -> str:
        """Create an image generation prompt from the decision"""
        
        base_prompt = f"""Professional marketing image for {context.get('brand_name', 'tech company')} 
launching {context.get('product_info', 'new product')}.
Style: Modern, clean, tech-forward.
Theme: {decision.get('decision', 'Innovation and progress')}.
"""
        
        # Simplify for better results
        simplified_prompt = f"{context.get('brand_name', 'tech')} {context.get('product_info', 'product')}, modern professional design, marketing photography"
        
        return simplified_prompt
    
    def generate_complete_post(self, decision: Dict, context: Dict, 
                               platform: str = "twitter", 
                               generate_image: bool = True) -> Dict:
        """Generate complete post with text and image"""
        
        print(f"\n📝 Generating {platform} post...")
        
        # Generate text
        post_data = self.generate_post_text(decision, context, platform)
        
        # Generate image if requested
        image_path = None
        if generate_image:
            image_prompt = self.create_image_prompt(decision, context)
            timestamp = int(time.time())
            image_path = self.generate_image(
                image_prompt, 
                filename=f"{platform}_post_{timestamp}.png"
            )
        
        post_data["image_path"] = image_path
        
        return post_data


def test_content_generator():
    """Test content generation"""
    
    print("Testing Content Generator...\n")
    
    generator = ContentGenerator()
    
    # Mock decision and context
    decision = {
        "decision": "Create bold, engaging post highlighting AI innovation",
        "implementation": "Platform: Twitter. Use trending hashtag #AIRevolution. Bold tone.",
        "winner": "viral_hunter"
    }
    
    context = {
        "brand_name": "TechFlow AI",
        "product_info": "Smart Scheduling Assistant - AI-powered calendar optimization",
        "target_audience": "Busy professionals and tech enthusiasts"
    }
    
    # Generate post (without image for quick test)
    post = generator.generate_complete_post(
        decision, 
        context, 
        platform="twitter",
        generate_image=False
    )
    
    print("\n✅ Generated Post:")
    print(f"Platform: {post['platform']}")
    print(f"Caption: {post['caption']}")
    print(f"Hashtags: {', '.join(post['hashtags'])}")
    print(f"Posting Time: {post['posting_time']}")
    print(f"Character Count: {post['char_count']}")


if __name__ == "__main__":
    test_content_generator()