import os
import json
import time
import requests
from dotenv import load_dotenv
from services.googlenews import GoogleNewsService
from services.official import OfficialService
from services.dashen import DashenService
from services.reddit_rss import RedditRSSService as RedditService
from services.translator import TranslationService
from datetime import datetime

# Load env
load_dotenv()

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history.json')

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_history(data):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def send_discord_webhook(webhook_url, content=None, embed=None):
    if not webhook_url:
        print("No Webhook URL provided.")
        return

    data = {}
    if content:
        data["content"] = content
    if embed:
        data["embeds"] = [embed]

    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Webhook sent successfully.")
        else:
            print(f"Webhook failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Webhook exception: {e}")

def main():
    # Configuration
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')

    if not WEBHOOK_URL:
        print("Missing WEBHOOK_URL in environment. Please check .env file.")
        return

    history = load_history()
    translator = TranslationService()
    
    # Define Stable Services to monitor
    services_to_check = [
        {
            "name": "Official Website",
            "instance": OfficialService(),
            "history_key": "last_official_time",
            "color": 15844367 # Gold
        },
        {
            "name": "17173.com",
            "instance": GoogleNewsService("燕云十六声"),
            "history_key": "last_google_news_time",
            "color": 16750848 # 17173 Orange
        },
        {
            "name": "NetEase Dashen",
            "instance": DashenService("c47870f2c5f142a58ea746fbc4655165"),
            "history_key": "last_dashen_time",
            "color": 15484743 # Dashen Red
        },
        {
            "name": "Reddit r/WhereWindsMeet",
            "instance": RedditService("WhereWindsMeet", post_limit=5),
            "history_key": "seen_reddit_wherewindsmeet_ids",
            "history_type": "ids",
            "color": 16729344 # Reddit Orange
        },
        {
            "name": "Reddit r/wherewindsmeet_",
            "instance": RedditService("wherewindsmeet_", post_limit=5),
            "history_key": "seen_reddit_wherewindsmeet_alt_ids",
            "history_type": "ids",
            "color": 16729344 # Reddit Orange
        }
    ]

    for svc in services_to_check:
        try:
            print(f"--- Checking {svc['name']} ---")
            # Determine default based on history type
            history_type = svc.get('history_type', 'timestamp')
            
            if history_type == 'ids':
                default_val = []
                last_check = history.get(svc['history_key'], default_val)
                # Ensure it's a list (in case of corruption or type change)
                if not isinstance(last_check, list):
                    last_check = []
            else:
                default_val = time.time() - 86400
                last_check = history.get(svc['history_key'], default_val)
                # Ensure it's a float
                if not isinstance(last_check, (int, float)):
                    last_check = default_val
            
            new_posts = svc['instance'].get_new_posts(last_check)
            
            if new_posts:
                print(f"Found {len(new_posts)} new posts from {svc['name']}.")
                for post in new_posts:
                    # Translate title and description
                    title_vn = translator.translate(post['title'], dest='vi', src='zh-cn')
                    
                    full_text = post.get('text', '')
                    description_vn = ""
                    if full_text:
                        # Translate full text
                        description_vn = translator.translate(full_text, dest='vi', src='zh-cn')
                        
                    # Format description for Discord (limit to ~1000 chars to be safe)
                    if len(description_vn) > 1000:
                        description_vn = f"{description_vn[:997]}..."
                    
                    description = f"{description_vn}\n\n[Xem thêm trên {svc['name']}]({post['link']})"

                    embed = {
                        "title": title_vn[:256],
                        "description": description,
                        "url": post['link'],
                        "color": svc.get("color", 3447003),
                        "timestamp": datetime.fromtimestamp(post['timestamp']).isoformat(),
                        "footer": {"text": f"Nguồn: {post['author']}"}
                    }
                    
                    send_discord_webhook(WEBHOOK_URL, embed=embed)
                    
                    # Update local history
                    if history_type == 'ids':
                        if svc['history_key'] not in history or not isinstance(history[svc['history_key']], list):
                            history[svc['history_key']] = []
                        history[svc['history_key']].append(post['post_id'])
                        
                        # Limit to last 50 IDs to prevent unlimited growth
                        if len(history[svc['history_key']]) > 50:
                            history[svc['history_key']] = history[svc['history_key']][-50:]
                    else:
                        history[svc['history_key']] = post['timestamp']
                
                save_history(history)
            else:
                print(f"No new posts from {svc['name']}.")
                
        except Exception as e:
            print(f"Error checking {svc['name']}: {e}")

if __name__ == "__main__":
    main()
