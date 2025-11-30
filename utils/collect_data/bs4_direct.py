import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
#from rapidocr_onnxruntime import RapidOCR
from io import BytesIO
from PIL import Image
import json
import time
from urllib.parse import urlparse, urljoin


class RedditScraperDirect:
    def __init__(self, user_agent: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        #self.ocr = RapidOCR() #for image comments
    
    def scrape_post(self, post_url: str, delay: float = 1.0) -> Dict:
        try:
            json_url = self._get_json_url(post_url)
            
            response = self.session.get(json_url, timeout=10)
            response.raise_for_status()
            
            json_data = response.json()
            
            post_data = self._parse_post_data(json_data)
            
            post_data['comments'] = self._parse_comments(json_data)
            
            post_data['ocr_results'] = []
            
            if self._is_image_url(post_data['url']):
                ocr_text = self._process_image(post_data['url'])
                if ocr_text:
                    post_data['ocr_results'].append({
                        'image_url': post_data['url'],
                        'extracted_text': ocr_text
                    })
            
            if post_data.get('gallery_images'):
                for image_url in post_data['gallery_images']:
                    time.sleep(delay)
                    ocr_text = self._process_image(image_url)
                    if ocr_text:
                        post_data['ocr_results'].append({
                            'image_url': image_url,
                            'extracted_text': ocr_text
                        })
            
            return post_data
            
        except requests.exceptions.RequestException as e:
            return {'error': f"Failed to fetch post: {str(e)}"}
        except json.JSONDecodeError as e:
            return {'error': f"Failed to parse JSON: {str(e)}"}
        except Exception as e:
            return {'error': f"Failed to scrape post: {str(e)}"}
    
    def _get_json_url(self, post_url: str) -> str:
        url = post_url.rstrip('/')
        
        if not url.endswith('.json'):
            url += '.json'
        
        return url
    
    def _parse_post_data(self, json_data: List) -> Dict:
        post_listing = json_data[0]['data']['children'][0]['data']
        
        post_data = {
            'post_id': post_listing.get('id'),
            'title': post_listing.get('title'),
            'author': post_listing.get('author', '[deleted]'),
            'score': post_listing.get('score', 0),
            'upvote_ratio': post_listing.get('upvote_ratio', 0),
            'num_comments': post_listing.get('num_comments', 0),
            'created_utc': post_listing.get('created_utc'),
            'subreddit': post_listing.get('subreddit'),
            'url': post_listing.get('url'),
            'selftext': post_listing.get('selftext', ''),
            'is_self': post_listing.get('is_self', False),
            'link_flair_text': post_listing.get('link_flair_text'),
            'permalink': f"https://www.reddit.com{post_listing.get('permalink')}",
            'thumbnail': post_listing.get('thumbnail'),
            'is_video': post_listing.get('is_video', False),
            'gallery_images': []
        }
        
        if 'gallery_data' in post_listing and 'media_metadata' in post_listing:
            media_metadata = post_listing['media_metadata']
            for item in post_listing['gallery_data']['items']:
                media_id = item['media_id']
                if media_id in media_metadata:
                    media_info = media_metadata[media_id]
                    if media_info.get('e') == 'Image' and 's' in media_info:
                        image_url = media_info['s'].get('u')
                        if image_url:
                            image_url = image_url.replace('&amp;', '&')
                            post_data['gallery_images'].append(image_url)
        
        if 'preview' in post_listing and 'images' in post_listing['preview']:
            for image in post_listing['preview']['images']:
                if 'source' in image:
                    source_url = image['source'].get('url', '').replace('&amp;', '&')
                    if source_url and source_url not in post_data['gallery_images']:
                        post_data['gallery_images'].append(source_url)
        
        return post_data
    
    def _parse_comments(self, json_data: List) -> List[Dict]:
        if len(json_data) < 2:
            return []
        
        comments_listing = json_data[1]['data']['children']
        return self._parse_comment_tree(comments_listing)
    
    def _parse_comment_tree(self, comments_data: List, parent_id: Optional[str] = None) -> List[Dict]:
        comments = []
        
        for item in comments_data:
            kind = item.get('kind')
            data = item.get('data', {})
            
            if kind == 'more':
                continue
            
            if kind == 't1':
                comment = {
                    'comment_id': data.get('id'),
                    'author': data.get('author', '[deleted]'),
                    'body': data.get('body', '[removed]'),
                    'score': data.get('score', 0),
                    'created_utc': data.get('created_utc'),
                    'parent_id': parent_id,
                    'is_submitter': data.get('is_submitter', False),
                    'distinguished': data.get('distinguished'),
                    'edited': data.get('edited', False),
                    'replies': []
                }
                
                if 'replies' in data and data['replies']:
                    if isinstance(data['replies'], dict):
                        replies_data = data['replies'].get('data', {}).get('children', [])
                        comment['replies'] = self._parse_comment_tree(
                            replies_data,
                            parent_id=comment['comment_id']
                        )
                
                comments.append(comment)
        
        return comments
    
    def _is_image_url(self, url: str) -> bool:
        if not url:
            return False
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        url_lower = url.lower()
        
        if any(url_lower.endswith(ext) for ext in image_extensions):
            return True
        
        image_hosts = ['i.redd.it', 'i.imgur.com', 'preview.redd.it']
        if any(host in url_lower for host in image_hosts):
            return True
        
        return False
    #also parse image into text with ocr
    def _process_image(self, image_url: str) -> Optional[str]:
        try:
            response = self.session.get(image_url, timeout=15)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                return None
            
            image = Image.open(BytesIO(response.content))
            
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            result, _ = self.ocr(image)
            
            if result:
                text_lines = [f"{line[1]} (confidence: {line[2]:.2f})" for line in result]
                return '\n'.join(text_lines)
            
            return None
            
        except Exception as e:
            print(f"OCR processing failed for {image_url}: {str(e)}")
            return None
    
    def scrape_post_html(self, post_url: str) -> Dict:
        try:
            response = self.session.get(post_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            post_data = {
                'title': None,
                'author': None,
                'selftext': None,
                'score': None,
                'comments': [],
                'ocr_results': [],
                'error': 'HTML parsing not fully implemented - use JSON method'
            }
            
            title_tag = soup.find('h1')
            if title_tag:
                post_data['title'] = title_tag.get_text(strip=True)
            
            return post_data
            
        except Exception as e:
            return {'error': f"Failed to scrape HTML: {str(e)}"}


def scrape_reddit_post(post_url: str, user_agent: Optional[str] = None) -> Dict:
    scraper = RedditScraperDirect(user_agent)
    return scraper.scrape_post(post_url)


if __name__ == "__main__":
    print("please see example.py")

