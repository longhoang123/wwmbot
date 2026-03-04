import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load env from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def send_telegram_message(bot_token, chat_id, text):
    if not bot_token or not chat_id:
        print("Error: No TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID found in .env")
        return False

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
            print("Successfully sent news to Telegram.")
            return True
        else:
            print(f"Failed to send: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Research Summary Data
    telegram_text = (
        "<b>Where Winds Meet (燕云十六声) - Latest Research Summary</b>\n\n"
        "<b>Key Releases</b>:\n"
        "- CN PC: Dec 27, 2024\n"
        "- CN Mobile: Jan 9, 2025\n"
        "- Global PC/PS5: Nov 14, 2025\n"
        "- Global Mobile: Dec 12, 2025\n\n"
        "<b>Stats & Achievements</b>:\n"
        "- 15 Million+ players in China.\n"
        "- Won 'Game of the Year' at 2025 TapTap Awards.\n"
        "- 9 Million+ international players within two weeks.\n\n"
        "<b>Upcoming</b>:\n"
        "- Jan 2026: New accessories, regions, and bosses.\n"
        "- April 2026: Major balance patch and competitive league.\n\n"
        "<a href='https://www.wherewindsmeetgame.com/'>Visit Official Site</a>\n\n"
        "<i>Automated Research Report | Feb 2026</i>"
    )

    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, telegram_text)

if __name__ == "__main__":
    main()
