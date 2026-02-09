import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.reddit import RedditService
from services.translator import TranslationService

def test_reddit_service():
    """Test Reddit service for both WhereWindsMeet subreddits."""
    
    subreddits = [
        ("WhereWindsMeet", 5),
        ("wherewindsmeet_", 5)
    ]
    
    translator = TranslationService()
    
    for subreddit, limit in subreddits:
        print(f"\n{'='*60}")
        print(f"Testing Reddit r/{subreddit}")
        print(f"{'='*60}\n")
        
        service = RedditService(subreddit, post_limit=limit)
        
        # Use timestamp from 7 days ago to get recent posts
        last_check = time.time() - (7 * 24 * 60 * 60)
        
        posts = service.get_new_posts(last_check)
        
        if posts:
            print(f"Found {len(posts)} posts:\n")
            
            for i, post in enumerate(posts, 1):
                print(f"Post {i}:")
                print(f"  Title: {post['title']}")
                
                # Translate title to Vietnamese
                try:
                    title_vn = translator.translate(post['title'], dest='vi', src='en')
                    print(f"  Title (VN): {title_vn}")
                except Exception as e:
                    print(f"  Translation error: {e}")
                
                print(f"  Author: {post['author']}")
                print(f"  Score: {post.get('score', 'N/A')}")
                print(f"  Link: {post['link']}")
                print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(post['timestamp']))}")
                
                if post['text']:
                    print(f"  Text: {post['text'][:100]}...")
                
                print()
        else:
            print(f"No posts found for r/{subreddit}")
    
    print(f"\n{'='*60}")
    print("Test completed!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    test_reddit_service()
