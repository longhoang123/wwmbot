import praw
import time
import os
from datetime import datetime

class RedditServicePRAW:
    def __init__(self, subreddit, post_limit=5):
        """
        Initialize Reddit service using PRAW (Python Reddit API Wrapper).
        
        Args:
            subreddit: Name of the subreddit (without r/)
            post_limit: Number of hot posts to fetch (default: 5)
            
        Note:
            Requires environment variables:
            - REDDIT_CLIENT_ID: Your Reddit app client ID
            - REDDIT_CLIENT_SECRET: Your Reddit app client secret
            - REDDIT_USER_AGENT: Your bot's user agent string
            
            To create a Reddit app:
            1. Go to https://www.reddit.com/prefs/apps
            2. Click "Create App" or "Create Another App"
            3. Fill in the form:
               - Name: WhereWindsMeetBot
               - App type: script
               - Description: Bot to monitor Where Winds Meet subreddit
               - Redirect URI: http://localhost:8080
            4. Save the client_id and client_secret
        """
        self.subreddit = subreddit
        self.post_limit = post_limit
        
        # Load credentials from environment variables
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "WhereWindsMeetBot/1.0")
        
        # Validate credentials
        if not client_id or not client_secret:
            raise ValueError(
                "Reddit API credentials not found. Please set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET environment variables. "
                "See REDDIT_SETUP.md for instructions."
            )
        
        # Initialize Reddit instance
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            self.reddit.read_only = True  # We only need to read, not post
        except Exception as e:
            print(f"Error initializing Reddit API: {e}")
            raise
        
    def get_new_posts(self, last_check_timestamp):
        """
        Fetch new hot posts from the subreddit.
        
        Args:
            last_check_timestamp: Unix timestamp of last check
            
        Returns:
            List of new posts with title, link, text, timestamp, and author
        """
        print(f"Checking Reddit r/{self.subreddit}")
        
        try:
            subreddit = self.reddit.subreddit(self.subreddit)
            new_posts = []
            
            # Fetch hot posts
            for submission in subreddit.hot(limit=self.post_limit):
                created_utc = submission.created_utc
                
                # Check if post is newer than last check
                if created_utc > last_check_timestamp:
                    # Prepare text content
                    text_content = submission.selftext if submission.selftext else f"Score: {submission.score} points"
                    
                    # Limit text length
                    if len(text_content) > 500:
                        text_content = text_content[:497] + "..."
                    
                    new_posts.append({
                        'title': submission.title,
                        'link': f"https://www.reddit.com{submission.permalink}",
                        'text': text_content,
                        'timestamp': created_utc,
                        'author': f"u/{submission.author.name if submission.author else 'Unknown'}",
                        'score': submission.score,
                        'post_id': submission.id
                    })
            
            # Sort by timestamp (oldest first)
            new_posts.sort(key=lambda x: x['timestamp'])
            
            print(f"Found {len(new_posts)} new posts from r/{self.subreddit}")
            return new_posts
            
        except Exception as e:
            print(f"Exception fetching Reddit r/{self.subreddit}: {e}")
            return []
