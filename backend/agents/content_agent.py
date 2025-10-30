"""
Content generation agent using Ollama LLMs.
"""
import requests
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class ContentAgent:
    """Agent for generating content ideas and topics."""
    
    def __init__(self, ollama_url: str = "http://ollama:11434", model: str = "llama2"):
        self.ollama_url = ollama_url
        self.model = model
    
    def generate_content_ideas(self, brand_data: Dict, count: int = 5) -> List[Dict]:
        """Generate content ideas for a brand."""
        try:
            niche = brand_data.get('niche', 'general')
            target_audience = brand_data.get('target_audience', 'general audience')
            
            prompt = f"""Generate {count} viral content ideas for a {niche} brand targeting {target_audience}.
            
For each idea, provide:
1. Title (catchy, under 60 characters)
2. Hook (first 3 seconds to grab attention)
3. Content type (educational/entertainment/viral)
4. Key points to cover

Format as JSON array."""
            
            response = self._call_ollama(prompt)
            
            # Parse and structure the response
            ideas = self._parse_content_ideas(response, count)
            
            logger.info(f"Generated {len(ideas)} content ideas for brand")
            return ideas
            
        except Exception as e:
            logger.error(f"Error generating content ideas: {e}")
            return self._fallback_ideas(count)
    
    def generate_hook(self, topic: str, niche: str) -> str:
        """Generate an attention-grabbing hook for a video."""
        try:
            prompt = f"""Create a viral hook (first 3 seconds) for a {niche} video about: {topic}

Requirements:
- Maximum 10 words
- Creates curiosity or urgency
- Stops scrolling
- No questions

Return only the hook text."""
            
            hook = self._call_ollama(prompt)
            return hook.strip()[:100]  # Limit length
            
        except Exception as e:
            logger.error(f"Error generating hook: {e}")
            return f"You won't believe this about {topic}!"
    
    def analyze_trend(self, topic: str) -> Dict:
        """Analyze a topic for viral potential."""
        try:
            prompt = f"""Analyze this topic for viral potential: {topic}

Provide:
1. Viral score (1-10)
2. Why it could go viral
3. Best platform (TikTok/Instagram/YouTube)
4. Target audience
5. Suggested posting time

Format as JSON."""
            
            response = self._call_ollama(prompt)
            
            return {
                'topic': topic,
                'viral_score': 7,  # Default
                'analysis': response,
                'recommended_platform': 'tiktok'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {'topic': topic, 'viral_score': 5, 'analysis': 'Error analyzing'}
    
    def _call_ollama(self, prompt: str, max_tokens: int = 500) -> str:
        """Call Ollama API."""
        try:
            url = f"{self.ollama_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.8
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise
    
    def _parse_content_ideas(self, response: str, count: int) -> List[Dict]:
        """Parse content ideas from LLM response."""
        ideas = []
        
        # Try to parse JSON if available
        try:
            import json
            parsed = json.loads(response)
            if isinstance(parsed, list):
                return parsed[:count]
        except:
            pass
        
        # Fallback: extract structured data from text
        lines = response.strip().split('\n')
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_idea:
                    ideas.append(current_idea)
                    current_idea = {}
            elif line.lower().startswith(('title:', '1.', 'idea')):
                current_idea['title'] = line.split(':', 1)[-1].strip()
            elif line.lower().startswith(('hook:', '2.')):
                current_idea['hook'] = line.split(':', 1)[-1].strip()
            elif 'type' in line.lower():
                current_idea['content_type'] = line.split(':', 1)[-1].strip()
        
        if current_idea:
            ideas.append(current_idea)
        
        return ideas[:count] if ideas else self._fallback_ideas(count)
    
    def _fallback_ideas(self, count: int) -> List[Dict]:
        """Fallback content ideas if generation fails."""
        templates = [
            {
                'title': "5 Things You Didn't Know About [Topic]",
                'hook': "Number 3 will blow your mind!",
                'content_type': 'educational'
            },
            {
                'title': "The Truth About [Topic] Nobody Tells You",
                'hook': "I wish I knew this sooner...",
                'content_type': 'educational'
            },
            {
                'title': "How to [Achieve Goal] in 30 Days",
                'hook': "This changed everything for me",
                'content_type': 'educational'
            },
            {
                'title': "Stop Doing [Wrong Thing] - Do This Instead",
                'hook': "You've been doing it all wrong",
                'content_type': 'educational'
            },
            {
                'title': "Watch This Before You [Action]",
                'hook': "This could save you hours...",
                'content_type': 'entertainment'
            }
        ]
        
        return templates[:count]
