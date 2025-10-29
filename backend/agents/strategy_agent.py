"""
Content strategy agent for planning and optimization.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StrategyAgent:
    """Agent for content strategy and planning."""
    
    def __init__(self):
        pass
    
    def create_content_calendar(self, 
                               brand_data: Dict,
                               days: int = 30,
                               posts_per_day: Dict = None) -> List[Dict]:
        """Create a content calendar for a brand."""
        try:
            posts_per_day = posts_per_day or {'tiktok': 2, 'instagram': 1, 'youtube': 0.5}
            platforms = brand_data.get('platforms', ['tiktok'])
            
            calendar = []
            start_date = datetime.now()
            
            for day in range(days):
                current_date = start_date + timedelta(days=day)
                
                for platform in platforms:
                    posts_count = posts_per_day.get(platform, 1)
                    
                    # Handle fractional posts (e.g., 0.5 = every other day)
                    if posts_count < 1:
                        if day % int(1 / posts_count) != 0:
                            continue
                        posts_count = 1
                    
                    for post_num in range(int(posts_count)):
                        # Calculate optimal posting time
                        post_time = self._get_optimal_time(platform, post_num)
                        
                        calendar.append({
                            'date': current_date.strftime('%Y-%m-%d'),
                            'time': post_time,
                            'platform': platform,
                            'content_type': self._suggest_content_type(day, platform),
                            'priority': self._calculate_priority(day, platform)
                        })
            
            logger.info(f"Created {len(calendar)} content slots for {days} days")
            return calendar
            
        except Exception as e:
            logger.error(f"Error creating content calendar: {e}")
            return []
    
    def optimize_posting_schedule(self, 
                                  platform: str,
                                  target_audience: str = "general") -> Dict:
        """Suggest optimal posting times for a platform."""
        optimal_times = {
            'tiktok': {
                'general': ['09:00', '12:00', '19:00'],
                'teens': ['15:00', '19:00', '21:00'],
                'adults': ['07:00', '12:00', '20:00']
            },
            'instagram': {
                'general': ['11:00', '14:00', '20:00'],
                'teens': ['16:00', '19:00', '21:00'],
                'adults': ['08:00', '12:00', '19:00']
            },
            'youtube': {
                'general': ['14:00', '18:00', '20:00'],
                'teens': ['15:00', '20:00'],
                'adults': ['12:00', '19:00']
            }
        }
        
        audience_key = 'general'
        if 'teen' in target_audience.lower():
            audience_key = 'teens'
        elif 'adult' in target_audience.lower():
            audience_key = 'adults'
        
        times = optimal_times.get(platform, {}).get(audience_key, ['12:00', '18:00'])
        
        return {
            'platform': platform,
            'optimal_times': times,
            'timezone': 'UTC',
            'best_days': self._get_best_days(platform)
        }
    
    def analyze_content_performance(self, videos: List[Dict]) -> Dict:
        """Analyze performance of posted videos."""
        if not videos:
            return {
                'total_videos': 0,
                'avg_views': 0,
                'avg_engagement_rate': 0,
                'recommendations': []
            }
        
        total_videos = len(videos)
        total_views = sum(v.get('views', 0) for v in videos)
        total_likes = sum(v.get('likes', 0) for v in videos)
        total_comments = sum(v.get('comments', 0) for v in videos)
        
        avg_views = total_views / total_videos if total_videos > 0 else 0
        avg_engagement = ((total_likes + total_comments) / total_views * 100) if total_views > 0 else 0
        
        # Analyze content types
        content_types = {}
        for video in videos:
            ctype = video.get('content_type', 'unknown')
            if ctype not in content_types:
                content_types[ctype] = {'count': 0, 'views': 0}
            content_types[ctype]['count'] += 1
            content_types[ctype]['views'] += video.get('views', 0)
        
        # Calculate average views per type
        for ctype in content_types:
            if content_types[ctype]['count'] > 0:
                content_types[ctype]['avg_views'] = (
                    content_types[ctype]['views'] / content_types[ctype]['count']
                )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            avg_views, avg_engagement, content_types
        )
        
        return {
            'total_videos': total_videos,
            'total_views': total_views,
            'avg_views': round(avg_views, 2),
            'avg_engagement_rate': round(avg_engagement, 2),
            'content_type_performance': content_types,
            'recommendations': recommendations
        }
    
    def suggest_improvements(self, brand_data: Dict, performance: Dict) -> List[str]:
        """Suggest improvements based on performance."""
        suggestions = []
        
        avg_views = performance.get('avg_views', 0)
        avg_engagement = performance.get('avg_engagement_rate', 0)
        
        if avg_views < 1000:
            suggestions.append("Focus on improving hooks - first 3 seconds are crucial")
            suggestions.append("Try more trending topics in your niche")
        
        if avg_engagement < 3:
            suggestions.append("Add more calls-to-action in your videos")
            suggestions.append("Ask questions to encourage comments")
        
        if avg_views > 0 and avg_engagement > 5:
            suggestions.append("Great engagement! Consider posting more frequently")
        
        # Content type suggestions
        content_types = performance.get('content_type_performance', {})
        if content_types:
            best_type = max(content_types.items(), 
                          key=lambda x: x[1].get('avg_views', 0))
            suggestions.append(f"Your '{best_type[0]}' content performs best - create more!")
        
        return suggestions
    
    def _get_optimal_time(self, platform: str, post_number: int = 0) -> str:
        """Get optimal posting time."""
        times = {
            'tiktok': ['09:00', '12:00', '19:00'],
            'instagram': ['11:00', '14:00', '20:00'],
            'youtube': ['14:00', '18:00']
        }
        
        platform_times = times.get(platform, ['12:00'])
        return platform_times[post_number % len(platform_times)]
    
    def _suggest_content_type(self, day: int, platform: str) -> str:
        """Suggest content type based on day and platform."""
        # Vary content types throughout the week
        types = ['educational', 'entertainment', 'viral']
        return types[day % len(types)]
    
    def _calculate_priority(self, day: int, platform: str) -> str:
        """Calculate content priority."""
        if day < 7:
            return 'high'
        elif day < 14:
            return 'medium'
        else:
            return 'low'
    
    def _get_best_days(self, platform: str) -> List[str]:
        """Get best days to post."""
        best_days = {
            'tiktok': ['Monday', 'Wednesday', 'Friday'],
            'instagram': ['Tuesday', 'Thursday', 'Sunday'],
            'youtube': ['Thursday', 'Friday', 'Saturday']
        }
        
        return best_days.get(platform, ['Monday', 'Wednesday', 'Friday'])
    
    def _generate_recommendations(self, 
                                 avg_views: float,
                                 avg_engagement: float,
                                 content_types: Dict) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        if avg_views < 500:
            recommendations.append("Views are low - focus on hook optimization")
        elif avg_views > 10000:
            recommendations.append("Excellent view count! Maintain consistency")
        
        if avg_engagement < 2:
            recommendations.append("Engagement is low - add more CTAs")
        elif avg_engagement > 5:
            recommendations.append("Great engagement rate!")
        
        if content_types:
            best_type = max(content_types.items(), key=lambda x: x[1].get('avg_views', 0))
            recommendations.append(f"Best performing: {best_type[0]} content")
        
        return recommendations
