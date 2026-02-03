from bs4 import BeautifulSoup
import feedparser
import time
import requests
from urllib.parse import quote

class GoogleNewsService:
    def __init__(self, keyword):
        # Broad search to ensure indexing
        self.keyword = keyword
        self.rss_url = f"https://news.google.com/rss/search?q={quote(keyword)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

    def resolve_google_link(self, google_url):
        try:
            response = requests.get(google_url, timeout=5)
            return response.url
        except:
            return google_url

    def get_post_content(self, link):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        try:
            resolved_link = self.resolve_google_link(link)
            response = requests.get(resolved_link, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"text": "", "link": resolved_link}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()

            paragraphs = soup.find_all('p')
            text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text()) > 20])
            
            return {
                "text": text[:1000], # Minimal text needed now
                "link": resolved_link
            }
        except:
            return {"text": "", "link": link}

    def get_new_posts(self, last_check_timestamp):
        print(f"Checking Google News RSS (filtered for 17173.com): {self.rss_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(self.rss_url, headers=headers, timeout=20)
            if response.status_code != 200:
                return []
            
            feed = feedparser.parse(response.text)
            new_posts = []
            
            # Google News RSS usually has the top entries first
            for entry in feed.entries[:50]: # Increased to find more matches
                if not hasattr(entry, 'published_parsed'):
                    continue
                
                # Filter for 17173 as requested
                source_name = getattr(entry, 'source', {}).get('title', '').lower() if hasattr(entry, 'source') else ""
                if '17173' not in entry.link.lower() and '17173' not in source_name:
                    continue

                entry_timestamp = time.mktime(entry.published_parsed)
                
                # Use a small buffer (5 min) to handle RSS indexing latency
                if entry_timestamp > last_check_timestamp:
                    content_details = self.get_post_content(entry.link)
                    
                    new_posts.append({
                        'title': entry.title,
                        'link': content_details['link'],
                        'text': content_details['text'],
                        'timestamp': entry_timestamp,
                        'author': '17173.com',
                        'images': [], # No images needed anymore
                        'videos': []
                    })

            new_posts.sort(key=lambda x: x['timestamp'])
            return new_posts
            
        except Exception as e:
             print(f"Exception fetching Google News RSS: {e}")
             return []
