import json
import time
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))
from bs4_direct import RedditScraperDirect


class MoviePostsParser:
    def __init__(self, top_comments_limit: int = 1):
        self.scraper = RedditScraperDirect()
        self.top_comments_limit = top_comments_limit
        
    def get_top_comments(self, comments, limit=5):
        """
        Extract top N comments based on score.
        Returns a flat list of top-level comments sorted by score.
        """
        if not comments:
            return []
        
        # Only get top-level comments (not nested replies)
        top_level_comments = [c for c in comments if c.get('parent_id') is None]
        
        # Sort by score descending
        sorted_comments = sorted(
            top_level_comments, 
            key=lambda x: x.get('score', 0), 
            reverse=True
        )
        
        # Get top N and format
        top_comments = []
        for comment in sorted_comments[:limit]:
            top_comments.append({
                'author': comment.get('author', '[deleted]'),
                'content': comment.get('body', ''),
                'score': comment.get('score', 0),
                'created_utc': comment.get('created_utc'),
                'is_submitter': comment.get('is_submitter', False)
            })
        
        return top_comments
    
    def parse_post(self, post_url: str):
        """
        Parse a single Reddit post and extract relevant information.
        """
        try:
            print(f"  Scraping: {post_url}")
            post_data = self.scraper.scrape_post(post_url, delay=1.0)
            
            # Check for errors
            if 'error' in post_data:
                print(f"    ⚠️  Error: {post_data['error']}")
                return None
            
            # Extract post ID from URL
            post_id = post_data.get('post_id', 'unknown')
            
            # Get top comments
            all_comments = post_data.get('comments', [])
            top_comments = self.get_top_comments(all_comments, self.top_comments_limit)
            
            # Format the result - only keep specified fields
            result = {
                'title': post_data.get('title', ''),
                'selftext': post_data.get('selftext', ''),
                'score': post_data.get('score', 0),
                'upvote_ratio': post_data.get('upvote_ratio', 0.0),
                'num_comments': post_data.get('num_comments', 0),
                'top_comment': top_comments[0] if top_comments else None
            }
            
            print(f"    ✓ Success: {result['score']} score, {'1 top comment' if result['top_comment'] else 'no comments'}")
            return result
            
        except Exception as e:
            print(f"    ✗ Exception: {str(e)}")
            return None
    
    def parse_movie_posts(self, movie_name: str, post_urls: list):
        """
        Parse posts for a single movie.
        """
        print(f"\n{'='*70}")
        print(f"Processing Movie: {movie_name}")
        print(f"{'='*70}")
        
        # Select first N posts
        selected_urls = post_urls
        print(f"Parsing {len(selected_urls)} posts...")
        
        posts = []
        successful = 0
        failed = 0
        
        for i, url in enumerate(selected_urls, 1):
            print(f"\n[{i}/{len(selected_urls)}]")
            
            post_data = self.parse_post(url)
            
            if post_data:
                posts.append(post_data)
                successful += 1
            else:
                failed += 1
            
            # Respectful delay between requests
            if i < len(selected_urls):
                time.sleep(2)
        
        print(f"\n{'─'*70}")
        print(f"Movie '{movie_name}' Complete:")
        print(f"  ✓ Successful: {successful}")
        print(f"  ✗ Failed: {failed}")
        print(f"{'─'*70}")
        
        return posts
    
    def parse_all_movies(self, search_results: dict):
        """
        Parse posts for all movies.
        """
        results = {}
        total_movies = len(search_results)
        
        print(f"\n{'#'*70}")
        print(f"STARTING DETAILED POST PARSING")
        print(f"{'#'*70}")
        print(f"Total Movies: {total_movies}")
        print(f"Top Comments per Post: {self.top_comments_limit}")
        print(f"{'#'*70}")
        
        for i, (movie_name, post_urls) in enumerate(search_results.items(), 1):
            print(f"\n\n{'█'*70}")
            print(f"MOVIE {i}/{total_movies}")
            print(f"{'█'*70}")
            
            posts = self.parse_movie_posts(movie_name, post_urls)
            
            results[movie_name] = {
                'num_posts': len(posts),
                'posts': posts
            }
            
            # Save incremental progress after each movie
            self.save_results(results, incremental=True)
            
            # Longer delay between movies
            if i < total_movies:
                print(f"\n⏸️  Waiting 5 seconds before next movie...")
                time.sleep(5)
        
        return results
    
    def save_results(self, results: dict, incremental: bool = False):
        """
        Save results to individual JSON files per movie.
        """
        import os
        
        output_dir = '/Users/eloisefreydier/Desktop/comp370 final project/COMP370FinalProj/data/parsed_movie_posts'
        
        if incremental:
            prefix = "💾 Saving incremental progress"
        else:
            prefix = "💾 Saving final results"
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save each movie to its own file
            for movie_name, movie_data in results.items():
                # Create a safe filename from the movie name
                safe_filename = movie_name.replace(' ', '_').replace('/', '_').replace(':', '_')
                output_file = os.path.join(output_dir, f"{safe_filename}.json")
                
                with open(output_file, 'w') as f:
                    json.dump({movie_name: movie_data}, f, indent=2)
                
                if not incremental:
                    print(f"✓ Saved {movie_name}: {output_file}")
        except Exception as e:
            print(f"✗ Error saving results: {str(e)}")


def main():
    # Load search results from the movie_search_results directory
    search_results = {}
    search_results_dir = '/Users/eloisefreydier/Desktop/comp370 final project/COMP370FinalProj/data/movie_search_results'
    
    print("Loading search results...")
    for json_file in Path(search_results_dir).glob('*.json'):
        with open(json_file, 'r') as f:
            movie_data = json.load(f)
            search_results.update(movie_data)
    
    print(f"✓ Loaded search results for {len(search_results)} movies")
    
    # Check which movies are already done
    output_dir = '/Users/eloisefreydier/Desktop/comp370 final project/COMP370FinalProj/data/parsed_movie_posts'
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    completed_movies = set()
    if os.path.exists(output_dir):
        for json_file in Path(output_dir).glob('*.json'):
            movie_name = json_file.stem.replace('_', ' ')
            completed_movies.add(movie_name)
    
    print(f"✓ Already completed: {len(completed_movies)} movies")
    if completed_movies:
        print(f"  {', '.join(list(completed_movies)[:3])}...")
    
    # Only process incomplete movies
    remaining_movies = {k: v for k, v in search_results.items() if k not in completed_movies}
    print(f"✓ Remaining to process: {len(remaining_movies)} movies")
    
    # Create parser and process remaining movies
    parser = MoviePostsParser(top_comments_limit=1)
    results = parser.parse_all_movies(remaining_movies)
    
    # Save results incrementally
    parser.save_results(results, incremental=True)
    
    # Print final summary
    print(f"\n\n{'#'*70}")
    print("FINAL SUMMARY")
    print(f"{'#'*70}")
    
    total_posts = 0
    total_comments = 0
    
    for movie_name, movie_data in results.items():
        posts_count = movie_data['num_posts']
        total_posts += posts_count
        
        # Count total top comments
        for post in movie_data['posts']:
            if post.get('top_comment'):
                total_comments += 1
        
        print(f"{movie_name}:")
        print(f"  Posts parsed: {posts_count}")
    
    print(f"\n{'─'*70}")
    print(f"Total Posts Parsed: {total_posts}")
    print(f"Total Top Comments Collected: {total_comments}")
    print(f"{'─'*70}")
    print(f"\n✅ All done! Check 'data/parsed_movie_posts/' directory for results.")
    print(f"{'#'*70}\n")


if __name__ == "__main__":
    main()

