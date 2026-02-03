import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from services.dashen import DashenService
from services.translator import TranslationService

def test_full_translation():
    user_id = "c47870f2c5f142a58ea746fbc4655165"
    service = DashenService(user_id)
    translator = TranslationService()
    
    # Check posts from last 48 hours to be sure we get something
    last_check = time.time() - (48 * 3600)
    print(f"Testing Full Translation with last_check = {datetime.fromtimestamp(last_check)}")
    
    posts = service.get_new_posts(last_check)
    
    print(f"\nFound {len(posts)} posts. Translating first one for preview:")
    if posts:
        post = posts[-1] # Newest
        print("-" * 30)
        print(f"Original Title: {post['title']}")
        title_vn = translator.translate(post['title'])
        print(f"Translated Title: {title_vn}")
        
        print(f"\nOriginal Text:\n{post['text'][:200]}...")
        text_vn = translator.translate(post['text'])
        print(f"\nTranslated Text:\n{text_vn}")
        print("-" * 30)
    else:
        print("No recent posts found to test translation.")

if __name__ == "__main__":
    test_full_translation()
