import feedparser
import time
import random
import requests
from datetime import datetime

class RedditRSSService:
    def __init__(self, subreddit, post_limit=5):
        """
        Initialize Reddit service using RSS feeds (no authentication required).
        
        Args:
            subreddit: Name of the subreddit (without r/)
            post_limit: Number of hot posts to fetch (default: 5)
        """
        self.subreddit = subreddit
        self.post_limit = post_limit
        # Use /top/.rss?t=day to get the highest upvoted posts of the day
        # This prioritizes high upvote counts as requested
        self.rss_url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t=day&limit={post_limit}"
        
    def get_new_posts(self, last_check):
        """
        Fetch new hot posts from the subreddit using RSS feed.
        
        Args:
            last_check: Unix timestamp (float) OR list of seen post IDs
            
        Returns:
            List of new posts with title, link, text, timestamp, and author
        """
        print(f"Checking Reddit r/{self.subreddit} via RSS")
        
        # Determine strict mode (timestamp) vs dedup mode (ids)
        seen_ids = set()
        min_timestamp = 0
        
        if isinstance(last_check, list):
            seen_ids = set(last_check)
        else:
            min_timestamp = float(last_check)
            
        try:
        # ... logic ...
            # Add random user agent to avoid simple blocking
            headers = {
                'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.0.0 Safari/537.36'
            }
            
            # Fetch RSS content manually first to handle headers better
            response = requests.get(self.rss_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Error fetching RSS for r/{self.subreddit}: HTTP {response.status_code}")
                # Try alternative URL format if first fails
                alt_url = f"https://old.reddit.com/r/{self.subreddit}/hot/.rss"
                print(f"Retrying with {alt_url}...")
                response = requests.get(alt_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    return []

            # Parse RSS content
            feed = feedparser.parse(response.content)
            
            new_posts = []
            
            # Iterate through entries
            # RSS feeds usually have ~25 entries, we take recent ones
            for entry in feed.entries:
                # Parse timestamp
                published_time = time.mktime(entry.published_parsed) if hasattr(entry, 'published_parsed') else time.time()
                
                # Extract link and ID
                link = entry.get('link', '')
                post_id = link.split('/comments/')[-1].split('/')[0] if '/comments/' in link else link
                
                is_new = False
                
                # Check if new based on mode
                if seen_ids:
                    # ID mode: New if ID not in seen list
                    if post_id and post_id not in seen_ids:
                        is_new = True
                else:
                    # Timestamp mode: New if newer than last check
                    if published_time > min_timestamp:
                        is_new = True
                
                if is_new:
                    # Extract information
                    title = entry.get('title', 'No Title')
                    author = entry.get('author', 'Unknown')
                    
                    # Get content
                    content = ''
                    if hasattr(entry, 'content'):
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                        
                    # Simple HTML cleanup (very basic)
                    import re
                    # Remove HTML tags
                    text_content = re.sub(r'<[^>]+>', '', content)
                    # Unescape entities
                    import html
                    text_content = html.unescape(text_content)
                    
                    # Limit text length
                    if len(text_content) > 500:
                        text_content = text_content[:497] + "..."
                    
                    
                    new_posts.append({
                        'title': title,
                        'link': link,
                        'text': text_content if text_content else "View post on Reddit",
                        'timestamp': published_time,
                        'author': author,
                        'score': 0,  # RSS doesn't provide score
                        'post_id': post_id
                    })
            
            # Sort by timestamp (oldest first)
            new_posts.sort(key=lambda x: x['timestamp'])
            
            # Apply limit after sorting to get the OLDEST new posts first, 
            # but we usually just return all new ones. 
            # If we want to strictly respect post_limit for the batch:
            if len(new_posts) > self.post_limit:
                new_posts = new_posts[:self.post_limit]
            
            print(f"Found {len(new_posts)} new posts from r/{self.subreddit}")
            return new_posts
            
        except Exception as e:
            print(f"Exception fetching Reddit RSS r/{self.subreddit}: {e}")
            return []
