import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote_plus
from typing import Dict, List


class RedditSearchScraper:
    def __init__(self, user_agent: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def search_movie(self, movie_name: str, max_links: int = 200) -> List[str]:
        """
        Search Reddit for a movie name and collect up to max_links post URLs.
        """
        print(f"\n{'='*60}")
        print(f"Searching for: {movie_name}")
        print(f"{'='*60}")
        
        links = []
        after = None  # Reddit's pagination token
        
        while len(links) < max_links:
            try:
                # Construct search URL with JSON endpoint
                search_query = quote_plus(movie_name)
                url = f"https://www.reddit.com/search.json?q={search_query}&sort=relevance&type=link"
                
                if after:
                    url += f"&after={after}"
                
                # Add delay to be respectful to Reddit's servers
                time.sleep(2)
                
                print(f"Fetching page (current links: {len(links)})...")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract posts from the response
                posts = data.get('data', {}).get('children', [])
                
                if not posts:
                    print(f"No more posts found. Total links collected: {len(links)}")
                    break
                
                # Extract permalink for each post
                for post in posts:
                    post_data = post.get('data', {})
                    permalink = post_data.get('permalink')
                    
                    if permalink:
                        full_url = f"https://www.reddit.com{permalink}"
                        links.append(full_url)
                        
                        if len(links) >= max_links:
                            break
                
                # Get pagination token for next page
                after = data.get('data', {}).get('after')
                
                if not after:
                    print(f"Reached end of results. Total links collected: {len(links)}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error: {str(e)}")
                break
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {str(e)}")
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        
        print(f"✓ Collected {len(links)} links for '{movie_name}'")
        return links[:max_links]  # Ensure we don't exceed max_links
    
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
    # movies_file = '/Users/bohan/Desktop/COMP370/COMP370FinalProj/data/all_selected_movies.json'
    movies_file = '/Users/bohan/Desktop/COMP370/COMP370FinalProj/data/select_movie.json'
    print("Loading movie names...")
    with open(movies_file, 'r') as f:
        movies = json.load(f)
    
    print(f"Loaded {len(movies)} movies: {', '.join(movies)}")
    
    # Create scraper and collect links
    scraper = RedditSearchScraper()
    results = scraper.scrape_all_movies(movies, max_links_per_movie=200)
    
    # Save results to individual JSON files
    output_dir = '/Users/bohan/Desktop/COMP370/COMP370FinalProj/data/movie_search_results'
    
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

