"""
Script writing agent for video content.
"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ScriptAgent:
    """Agent for writing video scripts."""
    
    def __init__(self, ollama_url: str = "http://ollama:11434", model: str = "llama2"):
        self.ollama_url = ollama_url
        self.model = model
    
    def write_script(self, 
                    title: str, 
                    hook: str,
                    content_type: str,
                    duration: int = 60,
                    character_personality: Optional[str] = None,
                    key_points: Optional[list] = None) -> Dict:
        """Write a complete video script."""
        try:
            personality = character_personality or "engaging and enthusiastic"
            points = key_points or []
            
            prompt = f"""Write a {duration}-second video script for:

Title: {title}
Hook: {hook}
Content Type: {content_type}
Personality: {personality}
{f"Key Points: {', '.join(points)}" if points else ""}

Requirements:
- Start with the hook
- Keep energy high
- Use simple language
- Include a call-to-action at the end
- Write for spoken word (natural, conversational)
- Aim for {duration} seconds when read aloud

Return only the script text."""
            
            script = self._call_ollama(prompt, max_tokens=800)
            
            # Post-process script
            script = self._format_script(script, hook)
            
            logger.info(f"Generated script for: {title}")
            
            return {
                'script': script,
                'word_count': len(script.split()),
                'estimated_duration': self._estimate_duration(script),
                'sections': self._identify_sections(script)
            }
            
        except Exception as e:
            logger.error(f"Error writing script: {e}")
            return {
                'script': self._fallback_script(title, hook),
                'word_count': 0,
                'estimated_duration': duration,
                'sections': ['intro', 'main', 'outro']
            }
    
    def improve_script(self, script: str, feedback: str) -> str:
        """Improve an existing script based on feedback."""
        try:
            prompt = f"""Improve this video script based on the feedback:

SCRIPT:
{script}

FEEDBACK:
{feedback}

Return the improved script only."""
            
            improved = self._call_ollama(prompt, max_tokens=800)
            return improved.strip()
            
        except Exception as e:
            logger.error(f"Error improving script: {e}")
            return script
    
    def generate_cta(self, platform: str, goal: str = "engagement") -> str:
        """Generate a call-to-action."""
        ctas = {
            'tiktok': {
                'engagement': "Double tap if you agree! 👆 Follow for more!",
                'follow': "Hit that follow button for daily content! ➕",
                'comment': "Comment below what you think! 💬"
            },
            'instagram': {
                'engagement': "Like and save this! Follow for more tips! ❤️",
                'follow': "Follow @[username] for daily content! 🔥",
                'comment': "Drop a comment below! 💬"
            },
            'youtube': {
                'engagement': "Like and subscribe for more! 👍",
                'follow': "Subscribe and hit the bell! 🔔",
                'comment': "Let me know in the comments! 💬"
            }
        }
        
        return ctas.get(platform, {}).get(goal, "Follow for more content!")
    
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
                    "temperature": 0.7
                }
            }
            
            response = requests.post(url, json=payload, timeout=45)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise
    
    def _format_script(self, script: str, hook: str) -> str:
        """Format and clean up the script."""
        # Ensure hook is at the beginning
        script = script.strip()
        
        if not script.lower().startswith(hook.lower()[:10]):
            script = f"{hook}\n\n{script}"
        
        # Clean up formatting
        script = '\n\n'.join(line.strip() for line in script.split('\n') if line.strip())
        
        return script
    
    def _estimate_duration(self, script: str) -> int:
        """Estimate video duration based on script."""
        # Average speaking rate: 150 words per minute
        word_count = len(script.split())
        duration = (word_count / 150) * 60  # Convert to seconds
        return int(duration)
    
    def _identify_sections(self, script: str) -> list:
        """Identify sections in the script."""
        sections = ['intro']
        
        paragraphs = script.split('\n\n')
        if len(paragraphs) > 2:
            sections.append('main')
        if len(paragraphs) > 3:
            sections.append('outro')
        
        return sections
    
    def _fallback_script(self, title: str, hook: str) -> str:
        """Fallback script if generation fails."""
        return f"""{hook}

In this video, I'm going to show you {title.lower()}.

This is something that can really make a difference, and I'm excited to share it with you.

Let me break it down for you step by step.

First, you need to understand the basics.

Then, we'll dive into the details.

And finally, I'll show you how to put it all together.

So let's get started!

If you found this helpful, make sure to follow for more content like this!"""
