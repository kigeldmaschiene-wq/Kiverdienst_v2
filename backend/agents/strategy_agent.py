"""
Strategy Agent - Content strategy and planning
"""
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StrategyAgent:
    """AI agent for content strategy and planning"""
    
    def __init__(self, model: str = "llama2", ollama_url: str = "http://ollama:11434"):
        self.model = model
        self.ollama_url = ollama_url
        logger.info(f"StrategyAgent initialized with model: {model}")
    
    def generate_content_calendar(self, 
                                 brand_name: str,
                                 niche: str,
                                 days: int = 7) -> List[Dict]:
        """
        Generate content calendar for specified days
        
        Args:
            brand_name: Name of the brand
            niche: Brand niche
            days: Number of days to plan
            
        Returns:
            List of content calendar entries
        """
        try:
            logger.info(f"Generating {days}-day content calendar for {brand_name}")
            
            calendar = []
            start_date = datetime.now()
            
            content_types = ['tutorial', 'story', 'tip', 'behind-scenes', 'trending']
            platforms = ['tiktok', 'instagram', 'youtube']
            
            for day in range(days):
                date = start_date + timedelta(days=day)
                
                entry = {
                    'date': date.strftime('%Y-%m-%d'),
                    'day_of_week': date.strftime('%A'),
                    'content_type': content_types[day % len(content_types)],
                    'platform': platforms[day % len(platforms)],
                    'topic': f"{niche} content for {date.strftime('%A')}",
                    'posting_time': '18:00',
                    'priority': 'high' if day < 3 else 'medium'
                }
                
                calendar.append(entry)
            
            logger.info(f"Generated calendar with {len(calendar)} entries")
            return calendar
            
        except Exception as e:
            logger.error(f"Error generating content calendar: {e}")
            return []
    
    def analyze_performance(self, videos: List[Dict]) -> Dict:
        """
        Analyze performance of videos
        
        Args:
            videos: List of video data
            
        Returns:
            Performance analysis
        """
        try:
            if not videos:
                return {
                    'total_videos': 0,
                    'average_views': 0,
                    'average_likes': 0,
                    'engagement_rate': 0
                }
            
            total_views = sum(v.get('views', 0) for v in videos)
            total_likes = sum(v.get('likes', 0) for v in videos)
            
            analysis = {
                'total_videos': len(videos),
                'total_views': total_views,
                'total_likes': total_likes,
                'average_views': total_views // len(videos) if videos else 0,
                'average_likes': total_likes // len(videos) if videos else 0,
                'engagement_rate': (total_likes / total_views * 100) if total_views > 0 else 0,
                'best_performing': max(videos, key=lambda x: x.get('views', 0)) if videos else None,
                'worst_performing': min(videos, key=lambda x: x.get('views', 0)) if videos else None
            }
            
            logger.info(f"Analyzed performance of {len(videos)} videos")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {}
    
    def recommend_posting_schedule(self, 
                                   platform: str,
                                   timezone: str = 'UTC') -> List[Dict]:
        """
        Recommend optimal posting times
        
        Args:
            platform: Social media platform
            timezone: Timezone for recommendations
            
        Returns:
            List of recommended posting times
        """
        try:
            # Platform-specific optimal times (general guidelines)
            schedules = {
                'tiktok': [
                    {'day': 'Monday', 'time': '18:00', 'reason': 'High engagement after work'},
                    {'day': 'Tuesday', 'time': '12:00', 'reason': 'Lunch break peak'},
                    {'day': 'Wednesday', 'time': '19:00', 'reason': 'Evening peak'},
                    {'day': 'Thursday', 'time': '17:00', 'reason': 'After school/work'},
                    {'day': 'Friday', 'time': '16:00', 'reason': 'Weekend anticipation'},
                    {'day': 'Saturday', 'time': '11:00', 'reason': 'Late morning browsing'},
                    {'day': 'Sunday', 'time': '13:00', 'reason': 'Afternoon relaxation'}
                ],
                'instagram': [
                    {'day': 'Monday', 'time': '11:00', 'reason': 'Mid-morning engagement'},
                    {'day': 'Tuesday', 'time': '14:00', 'reason': 'Afternoon peak'},
                    {'day': 'Wednesday', 'time': '15:00', 'reason': 'Mid-afternoon'},
                    {'day': 'Thursday', 'time': '11:00', 'reason': 'Morning peak'},
                    {'day': 'Friday', 'time': '10:00', 'reason': 'Weekend preparation'},
                    {'day': 'Saturday', 'time': '12:00', 'reason': 'Midday browsing'},
                    {'day': 'Sunday', 'time': '16:00', 'reason': 'Evening scroll'}
                ],
                'youtube': [
                    {'day': 'Monday', 'time': '14:00', 'reason': 'Post-lunch viewing'},
                    {'day': 'Tuesday', 'time': '15:00', 'reason': 'Afternoon viewing'},
                    {'day': 'Wednesday', 'time': '14:00', 'reason': 'Mid-week peak'},
                    {'day': 'Thursday', 'time': '16:00', 'reason': 'After work prep'},
                    {'day': 'Friday', 'time': '12:00', 'reason': 'Weekend start'},
                    {'day': 'Saturday', 'time': '09:00', 'reason': 'Morning viewers'},
                    {'day': 'Sunday', 'time': '11:00', 'reason': 'Sunday morning'}
                ]
            }
            
            schedule = schedules.get(platform.lower(), schedules['tiktok'])
            logger.info(f"Generated posting schedule for {platform}")
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error generating posting schedule: {e}")
            return []
    
    def suggest_optimization(self, video_data: Dict) -> List[str]:
        """
        Suggest optimizations for video performance
        
        Args:
            video_data: Video performance data
            
        Returns:
            List of optimization suggestions
        """
        try:
            suggestions = []
            
            views = video_data.get('views', 0)
            likes = video_data.get('likes', 0)
            engagement = (likes / views * 100) if views > 0 else 0
            
            if views < 1000:
                suggestions.append("Low views: Optimize title and thumbnail for better click-through")
            
            if engagement < 5:
                suggestions.append("Low engagement: Add stronger call-to-action in video")
            
            if not video_data.get('thumbnail_path'):
                suggestions.append("Missing thumbnail: Create eye-catching custom thumbnail")
            
            if len(video_data.get('title', '')) < 30:
                suggestions.append("Short title: Expand title to include relevant keywords")
            
            suggestions.append("Cross-post to multiple platforms for wider reach")
            suggestions.append("Engage with comments to boost algorithm performance")
            
            logger.info(f"Generated {len(suggestions)} optimization suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting optimizations: {e}")
            return []
