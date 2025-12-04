import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote_plus
from typing import Dict, List
from datetime import datetime

class RedditSearchScraper:
    def __init__(self, user_agent: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
     
    def is_highly_relevant_to_movie(self, title: str, selftext: str, movie_name: str) -> bool:
        """
        Only include posts that mention the movie AND contain movie-related keywords.
        """
        combined = (title + " " + selftext).lower()
        movie_lower = movie_name.lower()
        
        # Must contain the movie name
        if movie_lower not in combined:
            return False
        
        # Must contain at least one movie-related keyword
        movie_keywords = [
            'movie', 'film', 'release', 'theater', 'streaming', 'watch',
            'trailer', 'review', 'discussion', 'premiere', 'box office',
            'cast', 'director', 'actor', 'actress', 'imdb', 'cinema',
            'screening', 'dvd', 'blu-ray', 'netflix', 'hulu', 'disney',
            'amazon prime', 'plot', 'scene', 'ending', 'spoiler'
        ]
        
        has_movie_keyword = any(keyword in combined for keyword in movie_keywords)
        
        return has_movie_keyword
    
    def search_movie(self, movie_name: str, max_links: int = 500) -> List[str]:
        """Search Reddit with HIGH relevance filtering."""
        print(f"\nSearching for: {movie_name}")
        
        links = []
        after = None
        # the first movie was released on June 6: Ballerina so did -2 week
        movie_date_range_start = int(datetime(2025, 5, 23).timestamp())
        # last movie was released on July 2: Jurassic world so did +2 week
        movie_date_range_end = int(datetime(2025, 7, 16).timestamp())
        pages_checked = 0
        
        while len(links) < max_links and pages_checked < 20:  # Limit pages to avoid bad results
            try:
                search_query = quote_plus(f'"{movie_name}"')  # Exact phrase search
                url = f"https://www.reddit.com/search.json?q={search_query}&sort=relevance&t=year&type=link"

                
                if after:
                    url += f"&after={after}"
                
                time.sleep(3)
                pages_checked += 1
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                if not posts:
                    break
                
                for post in posts:
                    post_data = post.get('data', {})
                    created_utc = post_data.get('created_utc', 0)
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    permalink = post_data.get('permalink')
                    
                    # Filter 1: Date range (June-July 2025)
                    if not (movie_date_range_start <= created_utc < movie_date_range_end):
                        continue
                    
                    # Filter 2: HIGH relevance to THIS movie
                    if not self.is_highly_relevant_to_movie(title, selftext, movie_name):
                        continue
                    
                    if permalink:
                        full_url = f"https://www.reddit.com{permalink}"
                        links.append(full_url)
                        print(f"  ✓ Found: {title[:60]}...")
                        
                        if len(links) >= max_links:
                            break
                
                if len(links) >= max_links:
                    break
                
                after = data.get('data', {}).get('after')
                if not after:
                    break
                    
            except Exception as e:
                print(f"  ⚠️  Error: {str(e)}")
                break
        
        print(f"  ✓ Collected {len(links)} highly relevant posts")
        return links
    
    def scrape_all_movies(self, movies: List[str], max_links_per_movie: int = 200) -> Dict[str, List[str]]:
        """
        Search Reddit for all movies and return a dictionary mapping movie names to their links.
        """
        results = {}
        
        print(f"\n{'#'*60}")
        print(f"Starting Reddit search scraper for {len(movies)} movies")
        print(f"Target: {max_links_per_movie} links per movie")
        print(f"{'#'*60}")
        
        for i, movie in enumerate(movies, 1):
            print(f"\n[{i}/{len(movies)}] Processing: {movie}")
            links = self.search_movie(movie, max_links=max_links_per_movie)
            results[movie] = links
            
            # Add a longer delay between different movies
            if i < len(movies):
                print(f"\nWaiting 3 seconds before next movie...")
                time.sleep(3)
        
        return results


def main():
    # Load movie names from JSON file
    movies_file = r'C:\Users\Default\Desktop\COMP370FinalProj\data\all_selected_movies.json'
    print("Loading movie names...")
    with open(movies_file, 'r') as f:
        movies = json.load(f)
    
    print(f"Loaded {len(movies)} movies: {', '.join(movies)}")
    
    # Create scraper and collect links
    scraper = RedditSearchScraper()
    results = scraper.scrape_all_movies(movies, max_links_per_movie=200)
    
    # Save results to individual JSON files
    output_dir = r'C:\Users\Default\Desktop\COMP370FinalProj\data\movie_search_results'
    
    print(f"\n{'='*60}")
    print("Saving results to individual files...")
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each movie to its own file
    for movie, links in results.items():
        # Create a safe filename from the movie name
        safe_filename = movie.replace(' ', '_').replace('/', '_').replace(':', '_')
        output_file = os.path.join(output_dir, f"{safe_filename}.json")
        
        with open(output_file, 'w') as f:
            json.dump({movie: links}, f, indent=2)
        
        print(f"✓ Saved {movie}: {output_file}")
    

if __name__ == "__main__":
    main()

