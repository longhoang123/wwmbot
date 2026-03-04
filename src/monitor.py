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

def send_telegram_message(bot_token, chat_id, text):
    if not bot_token or not chat_id:
        print("Missing Telegram Bot Token or Chat ID.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Telegram failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Telegram exception: {e}")

def main():
    # Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment. Please check .env file.")
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
                        
                    # Format description for Telegram (limit to ~4000 chars to be safe)
                    if len(description_vn) > 3000:
                        description_vn = f"{description_vn[:2997]}..."
                    
                    description = f"{description_vn}\n\n<a href='{post['link']}'>Xem thêm trên {svc['name']}</a>"

                    telegram_text = f"<b>{title_vn[:256]}</b>\n\n{description}\n\n<i>Nguồn: {post['author']}</i>"
                    
                    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, telegram_text)
                    
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
