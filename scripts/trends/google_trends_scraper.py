"""
Google Trends Scraper - with fallback topics
"""
from datetime import datetime


class GoogleTrendsScraper:
    def __init__(self):
        self.fallback_topics = [
            "ChatGPT new features",
            "AI replacing jobs 2026",
            "Google Gemini update",
            "Meta AI latest news",
            "OpenAI GPT-5 release",
            "AI image generation tools",
            "Machine learning breakthroughs",
            "Tech layoffs AI automation",
            "Future of artificial intelligence",
            "Best AI tools 2026"
        ]

    def get_comprehensive_trends(self):
        """
        Try Google Trends first, use fallback if blocked
        """
        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl='en-US', tz=360)

            keywords = ['artificial intelligence', 'ChatGPT', 'AI technology']
            pytrends.build_payload(keywords, timeframe='now 1-d')
            interest = pytrends.interest_over_time()

            if not interest.empty:
                topics = list(interest.columns[:-1])
                print("✅ Google Trends fetched successfully!")
            else:
                topics = self.fallback_topics
                print("⚠️  Google Trends empty, using fallback topics")

        except Exception as e:
            print(f"⚠️  Google Trends blocked ({e}), using fallback topics")
            topics = self.fallback_topics

        summary = "## TRENDING AI/TECH TOPICS TODAY\n\n"
        for i, topic in enumerate(topics[:10], 1):
            summary += f"{i}. {topic}\n"

        return summary, {
            'trending_searches': topics[:10],
            'timestamp': datetime.now().isoformat()
        }
