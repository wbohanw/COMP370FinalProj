COMP 370 final project (to format later)
Project 2: Movie Release
Movie picked: Kpop Demon Hunters
## Reddit Scraper (Direct Web Scraping with OCR)

Scrapes Reddit posts and comments with direct scraping.
Automatically extracts text from images using RapidOCR.

### Quick Start

```bash
pip install -r requirements.txt
python example.py
```

### Run Scraper

```python
from utils.bs4_direct import RedditScraperDirect

scraper = RedditScraperDirect()
data = scraper.scrape_post("https://www.reddit.com/r/example/comments/...")

# Access scraped data
print(data['title'])           # Post title
print(data['comments'])        # All comments (nested)
print(data['ocr_results'])     # Text extracted from images
```