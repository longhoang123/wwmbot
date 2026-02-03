import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from services.dashen import DashenService

def test_dashen():
    user_id = "c47870f2c5f142a58ea746fbc4655165"
    service = DashenService(user_id)
    
    # Check posts from last 24 hours
    last_check = time.time() - (24 * 3600)
    print(f"Testing DashenService with last_check = {datetime.fromtimestamp(last_check)}")
    
    posts = service.get_new_posts(last_check)
    
    print(f"\nFound {len(posts)} new posts:")
    for post in posts:
        print("-" * 30)
        print(f"Title: {post['title']}")
        print(f"Time: {datetime.fromtimestamp(post['timestamp'])}")
        print(f"Link: {post['link']}")
        print(f"Text snippet: {post['text'][:100]}...")
        if post['images']:
            print(f"Images: {len(post['images'])} found")

if __name__ == "__main__":
    test_dashen()
