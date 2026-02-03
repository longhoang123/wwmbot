import os
import json
import time
import requests
from dotenv import load_dotenv
from services.googlenews import GoogleNewsService
from services.official import OfficialService
from services.dashen import DashenService
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
        }
    ]

    for svc in services_to_check:
        try:
            print(f"--- Checking {svc['name']} ---")
            # Default to 24h ago to avoid spam on first run if history is empty
            default_time = time.time() - 86400
            last_check = history.get(svc['history_key'], default_time)
            
            new_posts = svc['instance'].get_new_posts(last_check)
            
            if new_posts:
                print(f"Found {len(new_posts)} new posts from {svc['name']}.")
                for post in new_posts:
                    # Translate only the title
                    title_vn = translator.translate(post['title'], dest='vi', src='zh-cn')
                    
                    # Original text: only take the first few lines (~300 characters)
                    full_text = post.get('text', '')
                    lines = full_text.split('\n')
                    # Get first 3 non-empty lines for a cleaner look
                    preview_lines = [l.strip() for l in lines if l.strip()][:3]
                    description = "\n".join(preview_lines)
                    if len(description) > 300:
                        description = f"{description[:300]}..."
                    
                    description += f"\n\n[Xem thêm trên {svc['name']}]({post['link']})"

                    embed = {
                        "title": title_vn[:256],
                        "description": description,
                        "url": post['link'],
                        "color": svc.get("color", 3447003),
                        "timestamp": datetime.fromtimestamp(post['timestamp']).isoformat(),
                        "footer": {"text": f"Nguồn: {post['author']}"}
                    }
                    
                    # Image removal as requested by user
                    # if post.get('images') and len(post['images']) > 0:
                    #     embed["image"] = {"url": post['images'][0]}

                    send_discord_webhook(WEBHOOK_URL, embed=embed)
                    # Update local history
                    history[svc['history_key']] = post['timestamp']
                
                save_history(history)
            else:
                print(f"No new posts from {svc['name']}.")
                
        except Exception as e:
            print(f"Error checking {svc['name']}: {e}")

if __name__ == "__main__":
    main()
