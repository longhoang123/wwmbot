import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load env from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def send_discord_webhook(webhook_url, embed):
    if not webhook_url:
        print("Error: No WEBHOOK_URL found in .env")
        return False

    data = {"embeds": [embed]}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            print("Successfully sent news to Discord.")
            return True
        else:
            print(f"Failed to send: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    
    # Research Summary Data
    embed = {
        "title": "Where Winds Meet (燕云十六声) - Latest Research Summary",
        "description": (
            "**Key Releases**:\n"
            "- CN PC: Dec 27, 2024\n"
            "- CN Mobile: Jan 9, 2025\n"
            "- Global PC/PS5: Nov 14, 2025\n"
            "- Global Mobile: Dec 12, 2025\n\n"
            "**Stats & Achievements**:\n"
            "- 15 Million+ players in China.\n"
            "- Won 'Game of the Year' at 2025 TapTap Awards.\n"
            "- 9 Million+ international players within two weeks.\n\n"
            "**Upcoming**:\n"
            "- Jan 2026: New accessories, regions, and bosses.\n"
            "- April 2026: Major balance patch and competitive league."
        ),
        "url": "https://www.wherewindsmeetgame.com/",
        "color": 0x2b2d31, # Dark grey
        "timestamp": datetime.now().isoformat(),
        "footer": {"text": "Automated Research Report | Feb 2026"}
    }

    send_discord_webhook(WEBHOOK_URL, embed)

if __name__ == "__main__":
    main()
