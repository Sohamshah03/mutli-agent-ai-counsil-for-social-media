"""
Trend Intelligence Module
Fetches trending topics from Google Trends and Reddit
"""

import os
import json
import random
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Try to import trend APIs (graceful degradation if not available)
try:
    from pytrends.request import TrendReq
    GOOGLE_TRENDS_AVAILABLE = True
except ImportError:
    GOOGLE_TRENDS_AVAILABLE = False
    print("⚠️ pytrends not installed - Google Trends disabled")

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    print("⚠️ praw not installed - Reddit API disabled")


class TrendFetcher:
    """Fetch trending topics from multiple sources"""
    
    def __init__(self):
        self.google_trends = None
        self.reddit = None
        
        # Initialize Google Trends
        if GOOGLE_TRENDS_AVAILABLE:
            try:
                self.google_trends = TrendReq(hl='en-US', tz=360)
            except Exception as e:
                print(f"⚠️ Google Trends initialization failed: {e}")
        
        # Initialize Reddit
        if REDDIT_AVAILABLE:
            try:
                self.reddit = praw.Reddit(
                    client_id=os.getenv("REDDIT_CLIENT_ID"),
                    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                    user_agent=os.getenv("REDDIT_USER_AGENT", "AIMarketingCouncil/1.0")
                )
            except Exception as e:
                print(f"⚠️ Reddit initialization failed: {e}")
    
    def get_google_trends(self, keywords: List[str] = None, limit: int = 5) -> List[Dict]:
        """Fetch trending topics from Google Trends"""
        
        if not self.google_trends:
            return []
        
        try:
            if keywords:
                # Get interest over time for specific keywords
                self.google_trends.build_payload(keywords, timeframe='now 7-d')
                trending_data = self.google_trends.interest_over_time()
                
                trends = []
                for keyword in keywords:
                    if keyword in trending_data.columns:
                        avg_interest = trending_data[keyword].mean()
                        trends.append({
                            "topic": keyword,
                            "source": "google_trends",
                            "volume": "high" if avg_interest > 50 else "medium" if avg_interest > 20 else "low",
                            "relevance": min(avg_interest / 100, 1.0)
                        })
                
                return trends[:limit]
            else:
                # Get trending searches
                trending_searches = self.google_trends.trending_searches(pn='united_states')
                
                trends = []
                for topic in trending_searches[0][:limit]:
                    trends.append({
                        "topic": topic,
                        "source": "google_trends",
                        "volume": "high",
                        "relevance": 0.8  # Default relevance
                    })
                
                return trends
                
        except Exception as e:
            print(f"⚠️ Google Trends fetch failed: {e}")
            return []
    
    def get_reddit_trends(self, subreddits: List[str] = None, limit: int = 5) -> List[Dict]:
        """Fetch trending topics from Reddit"""
        
        if not self.reddit:
            return []
        
        if not subreddits:
            subreddits = ['technology', 'startups', 'marketing', 'socialmedia']
        
        try:
            trends = []
            
            for subreddit_name in subreddits:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get hot posts
                for post in subreddit.hot(limit=limit):
                    trends.append({
                        "topic": post.title,
                        "source": f"reddit_r/{subreddit_name}",
                        "volume": "high" if post.score > 1000 else "medium" if post.score > 100 else "low",
                        "relevance": min(post.score / 5000, 1.0),
                        "url": f"https://reddit.com{post.permalink}"
                    })
            
            # Sort by relevance and limit
            trends.sort(key=lambda x: x['relevance'], reverse=True)
            return trends[:limit]
            
        except Exception as e:
            print(f"⚠️ Reddit fetch failed: {e}")
            return []
    
    def get_sample_trends(self, limit: int = 10) -> List[Dict]:
        """Get sample trends from local data (fallback)"""
        
        try:
            with open('data/sample_trends.json', 'r') as f:
                data = json.load(f)
                trends = data['sample_trends']
                
                # Randomize and limit
                random.shuffle(trends)
                return trends[:limit]
        except Exception as e:
            print(f"⚠️ Sample trends load failed: {e}")
            # Hardcoded fallback
            return [
                {"topic": "AI Innovation", "source": "fallback", "volume": "high", "relevance": 0.9},
                {"topic": "Tech Startups", "source": "fallback", "volume": "medium", "relevance": 0.8},
                {"topic": "Digital Marketing", "source": "fallback", "volume": "high", "relevance": 0.85},
                {"topic": "Productivity Tools", "source": "fallback", "volume": "medium", "relevance": 0.75},
                {"topic": "Remote Work", "source": "fallback", "volume": "high", "relevance": 0.8},
            ]
    
    def fetch_all_trends(self, use_apis: bool = True, limit: int = 10) -> List[Dict]:
        """Fetch trends from all available sources"""
        
        all_trends = []
        
        if use_apis:
            # Try Google Trends
            google_trends = self.get_google_trends(
                keywords=['AI', 'technology', 'startup', 'innovation', 'productivity'],
                limit=5
            )
            all_trends.extend(google_trends)
            
            # Try Reddit
            reddit_trends = self.get_reddit_trends(
                subreddits=['technology', 'startups'],
                limit=5
            )
            all_trends.extend(reddit_trends)
        
        # If no API trends, use samples
        if not all_trends:
            print("ℹ️ Using sample trends (APIs unavailable)")
            all_trends = self.get_sample_trends(limit=limit)
        
        # Deduplicate and limit
        unique_trends = []
        seen_topics = set()
        
        for trend in all_trends:
            topic_normalized = trend['topic'].lower().strip()
            if topic_normalized not in seen_topics:
                seen_topics.add(topic_normalized)
                unique_trends.append(trend)
        
        return unique_trends[:limit]
    
    def format_trends_for_context(self, trends: List[Dict]) -> List[str]:
        """Format trends for agent context"""
        
        formatted = []
        for trend in trends:
            source = trend.get('source', 'unknown')
            volume = trend.get('volume', 'medium')
            topic = trend.get('topic', '')
            
            formatted.append(f"{topic} (Source: {source}, Volume: {volume})")
        
        return formatted


def test_trend_fetcher():
    """Test the trend fetcher"""
    
    print("Testing Trend Fetcher...\n")
    
    fetcher = TrendFetcher()
    
    print("Fetching trends...")
    trends = fetcher.fetch_all_trends(use_apis=True, limit=10)
    
    print(f"\n✅ Found {len(trends)} trends:\n")
    for i, trend in enumerate(trends, 1):
        print(f"{i}. {trend['topic']}")
        print(f"   Source: {trend['source']} | Volume: {trend['volume']} | Relevance: {trend.get('relevance', 'N/A')}")
    
    print("\nFormatted for agents:")
    formatted = fetcher.format_trends_for_context(trends)
    for trend in formatted[:5]:
        print(f"  - {trend}")


if __name__ == "__main__":
    test_trend_fetcher()