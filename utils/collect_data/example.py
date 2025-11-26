"""
Example usage of the Reddit direct web scraper
"""

from utils.bs4_direct import RedditScraperDirect
import json


scraper = RedditScraperDirect()

post_url = "https://www.reddit.com/r/Schaffrillas/comments/1lweugg/this_statements_even_funnier_now_that_kpop_demon/"

data = scraper.scrape_post(post_url)


filename = f"reddit_post_{data['post_id']}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"✅ Data saved to {filename}")


