import requests
import time
from datetime import datetime

class RedditService:
    def __init__(self, subreddit, post_limit=5):
        """
        Initialize Reddit service for a specific subreddit.
        
        Args:
            subreddit: Name of the subreddit (without r/)
            post_limit: Number of hot posts to fetch (default: 5)
        """
        self.subreddit = subreddit
        self.post_limit = post_limit
        self.base_url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        
    def get_new_posts(self, last_check_timestamp):
        """
        Fetch new hot posts from the subreddit.
        
        Args:
            last_check_timestamp: Unix timestamp of last check
            
        Returns:
            List of new posts with title, link, text, timestamp, and author
        """
        print(f"Checking Reddit r/{self.subreddit}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        
        params = {
            "limit": self.post_limit
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=20)
            
            if response.status_code != 200:
                print(f"Error fetching Reddit r/{self.subreddit}: HTTP {response.status_code}")
                return []
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            new_posts = []
            
            for post_data in posts:
                post = post_data.get('data', {})
                
                # Extract post information
                title = post.get('title', 'No Title')
                post_id = post.get('id', '')
                author = post.get('author', 'Unknown')
                score = post.get('score', 0)
                created_utc = post.get('created_utc', time.time())
                permalink = f"https://www.reddit.com{post.get('permalink', '')}"
                
                # Get post content
                selftext = post.get('selftext', '')
                url = post.get('url', permalink)
                
                # Check if post is newer than last check
                if created_utc > last_check_timestamp:
                    # Prepare text content
                    text_content = selftext if selftext else f"Score: {score} points"
                    
                    # Limit text length
                    if len(text_content) > 500:
                        text_content = text_content[:497] + "..."
                    
                    new_posts.append({
                        'title': title,
                        'link': permalink,
                        'text': text_content,
                        'timestamp': created_utc,
                        'author': f"u/{author}",
                        'score': score,
                        'post_id': post_id
                    })
            
            # Sort by timestamp (oldest first)
            new_posts.sort(key=lambda x: x['timestamp'])
            
            return new_posts
            
        except requests.exceptions.RequestException as e:
            print(f"Request error fetching Reddit r/{self.subreddit}: {e}")
            return []
        except Exception as e:
            print(f"Exception fetching Reddit r/{self.subreddit}: {e}")
            return []
