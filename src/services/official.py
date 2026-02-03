from bs4 import BeautifulSoup
import requests
import time
import re
from datetime import datetime

class OfficialService:
    def __init__(self):
        self.url = "https://www.yysls.cn/news/"
        self.api_url = "https://yysls.cn/news/index.json" 

    def get_post_content(self, link):
        """Scrape full content, images, and videos from a specific news page."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(link, headers=headers, timeout=20)
            if response.status_code != 200:
                return None
            
            # Fix encoding if necessary (NetEase often uses utf-8)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title extraction - usually in h1
            title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Official News"
            
            # Content extraction - look for common NetEase news body classes
            # Common classes: .content, .news-detail, .art_content, .main_content
            content_div = soup.select_one('.content, .news-detail, .art_content, .main_content, #content')
            
            if not content_div:
                # Fallback if no specific div found
                full_text = soup.get_text(separator='\n', strip=True)
                images = []
                videos = []
            else:
                # Extract text
                full_text = content_div.get_text(separator='\n', strip=True)
                
                # Extract images
                # NetEase often uses data-src or just src
                images = []
                for img in content_div.find_all('img'):
                    img_src = img.get('src') or img.get('data-src')
                    if img_src and img_src.startswith('http'):
                        images.append(img_src)
                
                # Extract videos
                videos = []
                # Check for <video> tags
                for v in content_div.find_all('video'):
                    v_src = v.get('src') or v.find('source').get('src') if v.find('source') else None
                    if v_src:
                        videos.append(v_src)
                
                # Check for iframes (often used for embedded players like Bilibili or NetEase's own)
                for f in content_div.find_all('iframe'):
                    f_src = f.get('src')
                    if f_src:
                        videos.append(f_src)

            return {
                'title': title,
                'text': full_text,
                'images': images,
                'videos': videos
            }
        except Exception as e:
            print(f"Error scraping post content: {e}")
            return None

    def get_new_posts(self, last_check_timestamp):
        print(f"Checking Official Website: {self.url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(self.url, headers=headers, timeout=20)
            if response.status_code != 200:
                print(f"Error fetching Official Site: HTTP {response.status_code}")
                return []
            
            links = re.findall(r'href="(https://www.yysls.cn/news/.*?\.html)"', response.text)
            new_posts = []
            
            seen = set()
            unique_links = [x for x in links if not (x in seen or seen.add(x))]
            
            for link in unique_links[:5]:
                date_match = re.search(r'/(\d{8})/', link)
                ts = time.time()
                if date_match:
                    try:
                        parsed_date = datetime.strptime(date_match.group(1), "%Y%m%d")
                        base_ts = parsed_date.timestamp()
                        
                        # Extract a stable offset from the ID in the link to differentiate posts on the same day
                        # Link pattern example: .../20260203/40412_1285159.html
                        id_match = re.search(r'(\d+)\.html$', link)
                        if id_match:
                            # Use the ID as a second-offset (modulo one day) to keep it stable and readable
                            # This ensures two posts on the same day have different but STABLE timestamps
                            offset = int(id_match.group(1)) % 86400
                            ts = base_ts + offset
                        else:
                            ts = base_ts
                    except:
                        ts = time.time() # Extreme fallback
                else:
                    ts = time.time()
                
                if ts > last_check_timestamp:
                    # Fetch full details
                    details = self.get_post_content(link)
                    if details:
                        new_posts.append({
                            'title': details['title'],
                            'link': link,
                            'text': details['text'],
                            'timestamp': ts,
                            'author': 'Official Site',
                            'images': details['images'],
                            'videos': details['videos']
                        })
                    else:
                        # Fallback simple record if scraping fails
                        new_posts.append({
                            'title': "Official News Update",
                            'link': link,
                            'text': "Could not scrape content.",
                            'timestamp': ts,
                            'author': 'Official Site',
                            'images': [],
                            'videos': []
                        })

            new_posts.sort(key=lambda x: x['timestamp'])
            return new_posts
            
        except Exception as e:
             print(f"Exception fetching Official Site: {e}")
             return []
