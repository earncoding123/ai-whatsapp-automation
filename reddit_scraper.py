"""
Reddit Trend Scraper
Fetches hot topics from AI/Tech subreddits
"""

import praw
import json
from datetime import datetime
from config.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_SUBREDDITS


class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
    
    def scrape_hot_topics(self, limit=10):
        """
        Scrape hot topics from AI/Tech subreddits
        """
        all_posts = []
        
        for subreddit_name in REDDIT_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for post in subreddit.hot(limit=limit):
                    all_posts.append({
                        'subreddit': subreddit_name,
                        'title': post.title,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'url': post.url,
                        'created_utc': datetime.fromtimestamp(post.created_utc).isoformat()
                    })
            except Exception as e:
                print(f"Error scraping r/{subreddit_name}: {e}")
                continue
        
        # Sort by engagement (score + comments)
        all_posts.sort(key=lambda x: x['score'] + x['num_comments'], reverse=True)
        
        return all_posts[:15]  # Return top 15
    
    def get_trending_summary(self):
        """
        Get a formatted summary of trending topics
        """
        posts = self.scrape_hot_topics()
        
        summary = "## TRENDING AI/TECH TOPICS TODAY\n\n"
        
        for i, post in enumerate(posts[:10], 1):
            summary += f"{i}. **{post['title']}**\n"
            summary += f"   - Subreddit: r/{post['subreddit']}\n"
            summary += f"   - Engagement: {post['score']} upvotes, {post['num_comments']} comments\n\n"
        
        return summary, posts


def main():
    """
    Test function
    """
    scraper = RedditScraper()
    summary, posts = scraper.get_trending_summary()
    
    print(summary)
    
    # Save to JSON
    with open('data/reddit_trends.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print(f"\n✅ Scraped {len(posts)} trending posts")


if __name__ == "__main__":
    main()
