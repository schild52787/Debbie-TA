"""Social media scraping service for dispute research"""
import praw
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

from config.settings import settings


class SocialMediaService:
    """Service for scraping social media for travel dispute strategies"""

    def __init__(self):
        # Initialize Reddit client
        if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )
        else:
            self.reddit = None

    def search_reddit_disputes(
        self,
        provider: str,
        issue_type: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search Reddit for dispute resolution strategies

        Args:
            provider: Airline/hotel name (e.g., "Delta", "Marriott")
            issue_type: Type of issue (e.g., "cancellation", "delay")
            limit: Maximum number of posts to return

        Returns:
            List of relevant Reddit posts
        """
        if not self.reddit:
            print("Reddit client not configured")
            return []

        results = []

        # Subreddits to search
        subreddits = settings.SOCIAL_MEDIA_SOURCES.get('reddit', [])

        # Build search query
        search_terms = [provider.lower(), issue_type.replace('_', ' ')]
        query = ' '.join(search_terms)

        try:
            for subreddit_name in subreddits:
                # Remove 'r/' prefix if present
                subreddit_name = subreddit_name.replace('r/', '')

                subreddit = self.reddit.subreddit(subreddit_name)

                # Search for relevant posts
                for post in subreddit.search(query, limit=limit, time_filter='year'):
                    post_data = self._parse_reddit_post(post, provider, issue_type)
                    if post_data:
                        results.append(post_data)

        except Exception as e:
            print(f"Error searching Reddit: {e}")

        return results

    def _parse_reddit_post(
        self,
        post,
        provider: str,
        issue_type: str
    ) -> Optional[Dict]:
        """Parse Reddit post and extract relevant information"""
        try:
            # Get post content
            title = post.title
            body = post.selftext
            url = f"https://reddit.com{post.permalink}"

            # Analyze post for success indicators
            success_indicators = [
                'resolved', 'success', 'got refund', 'compensation',
                'worked', 'approved', 'received', 'granted'
            ]

            text_lower = (title + ' ' + body).lower()
            has_success = any(indicator in text_lower for indicator in success_indicators)

            # Extract strategy if mentioned
            strategy = self._extract_strategy(body)

            # Get top comments for additional insights
            top_comments = []
            post.comments.replace_more(limit=0)
            for comment in post.comments[:5]:
                if hasattr(comment, 'body') and len(comment.body) > 50:
                    top_comments.append({
                        'text': comment.body,
                        'score': comment.score,
                        'author': str(comment.author)
                    })

            return {
                'source': 'reddit',
                'subreddit': post.subreddit.display_name,
                'title': title,
                'body': body[:500],  # Truncate long posts
                'url': url,
                'score': post.score,
                'num_comments': post.num_comments,
                'created_date': datetime.fromtimestamp(post.created_utc),
                'has_success': has_success,
                'strategy': strategy,
                'top_comments': top_comments,
                'provider': provider,
                'issue_type': issue_type,
            }

        except Exception as e:
            print(f"Error parsing Reddit post: {e}")
            return None

    def _extract_strategy(self, text: str) -> Optional[str]:
        """Extract dispute resolution strategy from text"""
        strategies = []

        # Common strategies to look for
        strategy_patterns = [
            (r'file.*?(EU 261|EU261)', 'File EU261 claim'),
            (r'(DOT|department of transportation).*?complaint', 'File DOT complaint'),
            (r'twitter.*?(@\w+)', 'Contact via Twitter'),
            (r'escalate.*?supervisor', 'Escalate to supervisor'),
            (r'credit card.*?(dispute|chargeback)', 'Credit card dispute/chargeback'),
            (r'small claims court', 'Small claims court'),
            (r'BBB.*?complaint', 'BBB complaint'),
        ]

        text_lower = text.lower()

        for pattern, strategy_name in strategy_patterns:
            if re.search(pattern, text_lower):
                strategies.append(strategy_name)

        return strategies[0] if strategies else None

    def get_successful_strategies(
        self,
        provider: str,
        issue_type: str,
        min_score: int = 5
    ) -> List[Dict]:
        """
        Get successful dispute resolution strategies from social media

        Args:
            provider: Airline/hotel name
            issue_type: Type of issue
            min_score: Minimum post score to consider

        Returns:
            List of successful strategies
        """
        posts = self.search_reddit_disputes(provider, issue_type, limit=50)

        # Filter for successful posts
        successful = [
            post for post in posts
            if post['has_success'] and post['score'] >= min_score
        ]

        # Sort by score (most upvoted first)
        successful.sort(key=lambda x: x['score'], reverse=True)

        return successful[:10]

    def scrape_flyertalk(
        self,
        provider: str,
        issue_type: str
    ) -> List[Dict]:
        """
        Scrape FlyerTalk forums for dispute strategies
        Note: This is a placeholder - actual implementation would use
        web scraping with BeautifulSoup/Scrapy

        Args:
            provider: Airline/hotel name
            issue_type: Type of issue

        Returns:
            List of relevant forum posts
        """
        # This would require web scraping implementation
        # Placeholder for now
        return []

    def generate_dispute_research_report(
        self,
        provider: str,
        issue_type: str
    ) -> Dict:
        """
        Generate comprehensive research report on dispute resolution

        Args:
            provider: Airline/hotel name
            issue_type: Type of issue

        Returns:
            Dictionary with research findings
        """
        # Get successful strategies from Reddit
        reddit_strategies = self.get_successful_strategies(provider, issue_type)

        # Analyze common strategies
        strategy_counts = {}
        for post in reddit_strategies:
            if post['strategy']:
                strategy_counts[post['strategy']] = strategy_counts.get(post['strategy'], 0) + 1

        # Get recommended strategies (most common)
        recommended_strategies = sorted(
            strategy_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        report = {
            'provider': provider,
            'issue_type': issue_type,
            'total_cases_found': len(reddit_strategies),
            'recommended_strategies': [
                {'strategy': strat, 'occurrences': count}
                for strat, count in recommended_strategies
            ],
            'successful_cases': reddit_strategies[:5],  # Top 5 most upvoted
            'generated_at': datetime.now().isoformat(),
        }

        return report

    def search_twitter_mentions(
        self,
        provider: str,
        keywords: List[str],
        limit: int = 10
    ) -> List[Dict]:
        """
        Search Twitter for mentions of provider + keywords
        Note: Requires Twitter API v2 credentials
        This is a placeholder for the actual implementation

        Args:
            provider: Airline/hotel name
            keywords: List of keywords to search
            limit: Maximum tweets to return

        Returns:
            List of relevant tweets
        """
        # This would require Twitter API v2 implementation
        # Placeholder for now
        return []


# Create singleton instance
social_media_service = SocialMediaService()
