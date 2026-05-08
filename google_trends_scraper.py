"""
Google Trends Scraper
Fetches trending AI/Tech topics from Google Trends
"""

from pytrends.request import TrendReq
import json
from datetime import datetime


class GoogleTrendsScraper:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    def get_trending_searches(self, country='united_states'):
        """
        Get daily trending searches
        """
        try:
            trending = self.pytrends.trending_searches(pn=country)
            trends_list = trending[0].tolist()[:20]  # Top 20
            
            return trends_list
        except Exception as e:
            print(f"Error fetching trending searches: {e}")
            return []
    
    def get_ai_tech_trends(self):
        """
        Get trends specifically related to AI and Technology
        """
        keywords = [
            'artificial intelligence',
            'ChatGPT',
            'AI technology',
            'machine learning',
            'tech news'
        ]
        
        try:
            self.pytrends.build_payload(
                keywords,
                timeframe='now 1-d',
                geo='',
                gprop=''
            )
            
            interest_over_time = self.pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                latest = interest_over_time.iloc[-1]
                trending_keywords = latest.sort_values(ascending=False).head(5)
                
                return [
                    {
                        'keyword': keyword,
                        'interest': int(value)
                    }
                    for keyword, value in trending_keywords.items()
                    if keyword != 'isPartial'
                ]
            
            return []
        except Exception as e:
            print(f"Error fetching AI/Tech trends: {e}")
            return []
    
    def get_related_queries(self, topic='artificial intelligence'):
        """
        Get related rising queries for a topic
        """
        try:
            self.pytrends.build_payload(
                [topic],
                timeframe='now 7-d',
                geo='',
                gprop=''
            )
            
            related_queries = self.pytrends.related_queries()
            
            if topic in related_queries and related_queries[topic]['rising'] is not None:
                rising = related_queries[topic]['rising'].head(10)
                return rising['query'].tolist()
            
            return []
        except Exception as e:
            print(f"Error fetching related queries: {e}")
            return []
    
    def get_comprehensive_trends(self):
        """
        Get a comprehensive summary of current trends
        """
        trending_searches = self.get_trending_searches()
        ai_trends = self.get_ai_tech_trends()
        related = self.get_related_queries()
        
        summary = "## GOOGLE TRENDS - AI/TECH TODAY\n\n"
        
        summary += "### Top Trending Searches:\n"
        for i, search in enumerate(trending_searches[:10], 1):
            summary += f"{i}. {search}\n"
        
        summary += "\n### AI/Tech Interest:\n"
        for trend in ai_trends:
            summary += f"- {trend['keyword']}: {trend['interest']}/100\n"
        
        summary += "\n### Rising AI Queries:\n"
        for query in related[:5]:
            summary += f"- {query}\n"
        
        return summary, {
            'trending_searches': trending_searches[:10],
            'ai_trends': ai_trends,
            'related_queries': related[:5],
            'timestamp': datetime.now().isoformat()
        }


def main():
    """
    Test function
    """
    scraper = GoogleTrendsScraper()
    summary, data = scraper.get_comprehensive_trends()
    
    print(summary)
    
    # Save to JSON
    with open('data/google_trends.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Google Trends data saved")


if __name__ == "__main__":
    main()
