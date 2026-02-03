from bs4 import BeautifulSoup
import requests
import time
import re
from datetime import datetime, timedelta

class DashenService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.profile_url = f"https://ds.163.com/user/{user_id}/"
        self.base_feed_url = "https://ds.163.com/feed/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://ds.163.com/",
        }

    def _parse_chinese_time(self, time_str):
        """Convert Chinese relative time strings into a UNIX timestamp."""
        now = datetime.now()
        time_str = time_str.strip()
        
        try:
            # 4小时前 (4 hours ago)
            h_match = re.search(r'(\d+)小时前', time_str)
            if h_match:
                return (now - timedelta(hours=int(h_match.group(1)))).timestamp()
            
            # 10分钟前 (10 minutes ago)
            m_match = re.search(r'(\d+)分钟前', time_str)
            if m_match:
                return (now - timedelta(minutes=int(m_match.group(1)))).timestamp()
            
            # 刚刚 (Just now)
            if "刚刚" in time_str:
                return now.timestamp()
            
            # 昨天 23:58 (Yesterday HH:MM)
            y_match = re.search(r'昨天\s*(\d{1,2}):(\d{2})', time_str)
            if y_match:
                yesterday = now - timedelta(days=1)
                return yesterday.replace(hour=int(y_match.group(1)), minute=int(y_match.group(2)), second=0, microsecond=0).timestamp()

            # 前天 23:58 (Day before yesterday)
            by_match = re.search(r'前天\s*(\d{1,2}):(\d{2})', time_str)
            if by_match:
                before_yesterday = now - timedelta(days=2)
                return before_yesterday.replace(hour=int(by_match.group(1)), minute=int(by_match.group(2)), second=0, microsecond=0).timestamp()

            # MM-DD / M/D / MM/DD
            # Cases like 1/31 or 01-31
            date_match = re.search(r'(\d{1,2})[/-](\d{1,2})', time_str)
            if date_match:
                month = int(date_match.group(1))
                day = int(date_match.group(2))
                # Assume current year
                year = now.year
                # If parsed date is in future, it's likely from last year
                dt = datetime(year, month, day)
                if dt > now:
                    dt = dt.replace(year=year-1)
                return dt.timestamp()
            
            # YYYY-MM-DD
            full_date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', time_str)
            if full_date_match:
                return datetime.strptime(full_date_match.group(0).replace('/', '-'), "%Y-%m-%d").timestamp()

        except Exception as e:
            print(f"Error parsing time '{time_str}': {e}")
            
        return now.timestamp() # Fallback

    def get_new_posts(self, last_check_timestamp):
        print(f"Checking Dashen User: {self.user_id}")
        
        try:
            response = requests.get(self.profile_url, headers=self.headers, timeout=20)
            if response.status_code != 200:
                print(f"Error fetching Dashen: HTTP {response.status_code}")
                return []
            
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all feed cards
            cards = soup.select('.feed-card')
            new_posts = []
            
            for card in cards:
                try:
                    feed_id = card.get('id')
                    if not feed_id:
                        continue
                    
                    # Title
                    title_div = card.select_one('.feed-card__content-title')
                    title = title_div.get_text(strip=True) if title_div else "Dashen Update"
                    
                    # Extract stable timestamp from ID (MongoDB ObjectId)
                    ts = None
                    if feed_id and len(feed_id) >= 8:
                        try:
                            ts = int(feed_id[:8], 16)
                        except (ValueError, TypeError):
                            pass
                    
                    # Fallback to fuzzy time
                    if ts is None:
                        time_tag = card.select_one('time.time-location__time')
                        time_str = time_tag.get_text(strip=True) if time_tag else ""
                        ts = self._parse_chinese_time(time_str)
                    
                    if ts > last_check_timestamp:
                        # Content text
                        content_div = card.select_one('.feed-text')
                        text = content_div.get_text(separator='\n', strip=True) if content_div else ""
                        
                        # Images
                        images = []
                        # Some images are in img tags, some in div backgrounds
                        for img in card.select('img'):
                            src = img.get('src') or img.get('data-src')
                            if src and src.startswith('http') and 'thumbnail' not in src:
                                images.append(src)
                        
                        new_posts.append({
                            'title': title,
                            'link': f"{self.base_feed_url}{feed_id}/",
                            'text': text,
                            'timestamp': ts,
                            'author': 'NetEase Dashen',
                            'images': images,
                            'videos': [] # Can add video extraction later if needed
                        })
                except Exception as e:
                    print(f"Error parsing card: {e}")
                    continue

            new_posts.sort(key=lambda x: x['timestamp'])
            return new_posts
            
        except Exception as e:
             print(f"Exception fetching Dashen: {e}")
             return []
