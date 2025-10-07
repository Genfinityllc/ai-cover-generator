#!/usr/bin/env python3
"""
Article-to-Prompt Generator for AI Cover Generation
Analyzes article content and generates sophisticated prompts for cover generation
"""

import openai
import os
import json
from typing import Dict, Optional, List

class ArticlePromptGenerator:
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass directly.")
        
        openai.api_key = self.api_key
        
        # Client-specific enhancement keywords
        self.client_enhancements = {
            "hedera": {
                "logo_elements": "Hedera H logo symbols, hexagonal patterns, hashgraph network visualization",
                "brand_colors": "purple and blue gradient, Hedera brand colors",
                "tech_concepts": "hashgraph technology, DAG structure, distributed ledger"
            },
            "algorand": {
                "logo_elements": "Algorand triangular logo symbols, geometric A elements, clean triangular patterns", 
                "brand_colors": "teal and black, Algorand brand colors",
                "tech_concepts": "pure proof of stake, consensus mechanism, Layer-1 blockchain"
            },
            "constellation": {
                "logo_elements": "Constellation star logo symbols, cosmic star patterns, stellar network design",
                "brand_colors": "cosmic blue and purple, space-themed colors",
                "tech_concepts": "DAG technology, stellar network, microservice architecture"
            }
        }
    
    def analyze_article_content(self, article_text: str, client: str = "hedera") -> Dict:
        """Analyze article content to extract key themes and concepts"""
        
        analysis_prompt = f"""
        Analyze this cryptocurrency/blockchain article and extract key information for creating a professional cover image:

        Article Content:
        {article_text[:3000]}  # Limit to first 3000 chars

        Please provide a JSON response with the following structure:
        {{
            "main_topic": "Primary subject of the article",
            "key_concepts": ["concept1", "concept2", "concept3"],
            "technology_focus": "Specific technology mentioned (DeFi, NFT, consensus, etc.)",
            "mood": "professional/exciting/innovative/technical/futuristic",
            "visual_elements": ["element1", "element2", "element3"],
            "article_type": "news/announcement/technical/analysis/partnership"
        }}

        Focus on elements that would translate well into visual design for a {client} branded article cover.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing cryptocurrency articles and extracting visual design concepts. Always respond with valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._create_fallback_analysis(article_text)
                
        except Exception as e:
            print(f"⚠️  OpenAI analysis failed: {e}")
            return self._create_fallback_analysis(article_text)
    
    def _create_fallback_analysis(self, article_text: str) -> Dict:
        """Create basic analysis when OpenAI fails"""
        words = article_text.lower()
        
        # Simple keyword detection
        concepts = []
        if "defi" in words: concepts.append("decentralized finance")
        if "nft" in words: concepts.append("NFT technology") 
        if "blockchain" in words: concepts.append("blockchain technology")
        if "consensus" in words: concepts.append("consensus mechanism")
        if "smart contract" in words: concepts.append("smart contracts")
        
        return {
            "main_topic": "Cryptocurrency Technology",
            "key_concepts": concepts[:3] if concepts else ["blockchain", "technology", "innovation"],
            "technology_focus": "blockchain technology",
            "mood": "professional",
            "visual_elements": ["network", "technology", "digital"],
            "article_type": "news"
        }
    
    def generate_enhanced_prompt(self, article_analysis: Dict, client: str = "hedera", title: str = "", subtitle: str = "") -> str:
        """Generate sophisticated prompt based on article analysis"""
        
        client_data = self.client_enhancements.get(client, self.client_enhancements["hedera"])
        
        prompt_generation_request = f"""
        Create a sophisticated Stable Diffusion XL prompt for a professional cryptocurrency article cover with these specifications:

        Article Analysis:
        - Main Topic: {article_analysis.get('main_topic', 'Cryptocurrency')}
        - Key Concepts: {', '.join(article_analysis.get('key_concepts', []))}
        - Technology Focus: {article_analysis.get('technology_focus', 'blockchain')}
        - Mood: {article_analysis.get('mood', 'professional')}
        - Visual Elements: {', '.join(article_analysis.get('visual_elements', []))}
        - Article Type: {article_analysis.get('article_type', 'news')}

        Client Branding Requirements:
        - Client: {client.upper()}
        - Logo Elements: {client_data['logo_elements']}
        - Brand Colors: {client_data['brand_colors']}
        - Tech Concepts: {client_data['tech_concepts']}

        Title: {title}
        Subtitle: {subtitle}

        Generate a detailed prompt that:
        1. Incorporates the article's specific themes and concepts
        2. Features prominent {client} logo elements and branding
        3. Creates a professional, high-quality background suitable for text overlay
        4. Matches the mood and technology focus of the article
        5. Uses appropriate colors and visual metaphors

        Response should be a single, detailed prompt (no JSON, just the prompt text).
        Include specific mentions of {client} branding elements.
        End with: "professional article cover background, no text overlays, no readable text, 8k resolution"
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed, specific prompts for AI image generation focused on cryptocurrency and blockchain themes. Create prompts that will generate professional, branded article covers."},
                    {"role": "user", "content": prompt_generation_request}
                ],
                max_tokens=400,
                temperature=0.4
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            
            # Ensure the prompt includes required elements
            if "no text" not in enhanced_prompt.lower():
                enhanced_prompt += ", professional article cover background, no text overlays, no readable text, 8k resolution"
            
            return enhanced_prompt
            
        except Exception as e:
            print(f"⚠️  OpenAI prompt generation failed: {e}")
            return self._create_fallback_prompt(article_analysis, client)
    
    def _create_fallback_prompt(self, analysis: Dict, client: str) -> str:
        """Create fallback prompt when OpenAI fails"""
        client_data = self.client_enhancements.get(client, self.client_enhancements["hedera"])
        
        main_topic = analysis.get('main_topic', 'cryptocurrency technology')
        mood = analysis.get('mood', 'professional')
        
        fallback_prompt = f"""
        {mood} {main_topic} background featuring {client_data['logo_elements']}, 
        incorporating {client_data['tech_concepts']}, with {client_data['brand_colors']}, 
        {' '.join(analysis.get('visual_elements', ['technology', 'network']))}, 
        high-quality digital art, professional article cover background, 
        no text overlays, no readable text, 8k resolution
        """
        
        return ' '.join(fallback_prompt.split())
    
    def process_article_for_cover(self, article_text: str, title: str, subtitle: str, client: str = "hedera") -> Dict:
        """Complete pipeline: article -> analysis -> enhanced prompt"""
        
        print(f"🔍 Analyzing article content for {client.upper()} cover generation...")
        
        # Step 1: Analyze article
        analysis = self.analyze_article_content(article_text, client)
        print(f"📊 Article analysis complete:")
        print(f"   Topic: {analysis.get('main_topic', 'N/A')}")
        print(f"   Focus: {analysis.get('technology_focus', 'N/A')}")
        print(f"   Mood: {analysis.get('mood', 'N/A')}")
        
        # Step 2: Generate enhanced prompt
        enhanced_prompt = self.generate_enhanced_prompt(analysis, client, title, subtitle)
        print(f"🎨 Enhanced prompt generated ({len(enhanced_prompt)} characters)")
        
        return {
            "analysis": analysis,
            "enhanced_prompt": enhanced_prompt,
            "client": client,
            "title": title,
            "subtitle": subtitle
        }

def main():
    """Test the article prompt generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Article-to-Prompt Generator")
    parser.add_argument("--article", type=str, required=True, help="Article text or file path")
    parser.add_argument("--title", type=str, default="Crypto Innovation", help="Article title")
    parser.add_argument("--subtitle", type=str, default="Technology Update", help="Article subtitle")
    parser.add_argument("--client", type=str, default="hedera", choices=["hedera", "algorand", "constellation"], help="Client brand")
    
    args = parser.parse_args()
    
    # Check if article is a file path or direct text
    if os.path.exists(args.article):
        with open(args.article, 'r') as f:
            article_text = f.read()
    else:
        article_text = args.article
    
    # Generate prompt
    generator = ArticlePromptGenerator()
    result = generator.process_article_for_cover(article_text, args.title, args.subtitle, args.client)
    
    print(f"\n✅ Enhanced Prompt:")
    print(f"{result['enhanced_prompt']}")

if __name__ == "__main__":
    main()