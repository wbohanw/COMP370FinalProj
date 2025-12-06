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

## Data collection

- **`data/collected_data/`** - Individual JSON files for each movie containing scraped posts and comments
  - `28_Years_Later.json`
  - `Ballerina.json`
  - `Bride_Hard.json`
  - `Jurassic_World_Rebirth.json`
  - `Elio.json`
  - `F1_The_Movie.json`
  - `The_Old_Guard_2.json`
  - `How_to_Train_Your_Dragon.json`
  - `Kpop_Demon_Hunters.json`
  - `M3GAN_2.0.json`
  - `Materialists.json`

- **`data/pre-data/`** - Search results and preliminary data
  - `main_movie_search_results.json` - Reddit post URLs for main movie
  - `reddit_movie_search_results.json` - Reddit post URLs for all movies

- **`data/backup/`** - Backup copies of collected data

- **`data/all_selected_movies.json`** - List of all movies being analyzed
- **`data/main_movie.json`** - Primary movie focus (Kpop Demon Hunters)

