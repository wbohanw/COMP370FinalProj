import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import re

class UTCDateConverter:
    def __init__(self, parsed_posts_dir: str, output_excel: str):
        self.parsed_posts_dir = parsed_posts_dir
        self.output_excel = output_excel
        self.all_posts = []
    
    def clean_text(self, text):
        """Clean and normalize Reddit post text for Excel."""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\n\n+', '\n', text)  # Multiple newlines to single
        text = re.sub(r'\t+', ' ', text)      # Tabs to spaces
        text = text.strip()
        
        # Remove special Unicode characters that cause Excel issues
        text = text.encode('utf-8', 'ignore').decode('utf-8')
        
        # Limit text length to prevent Excel cell overflow
        if len(text) > 32767:  # Excel cell limit
            text = text[:32700] + "..."
        
        return text
    
    def convert_utc_to_datetime(self, utc_timestamp):
        """Convert UTC timestamp to readable datetime string."""
        if utc_timestamp is None:
            return None
        try:
            return datetime.utcfromtimestamp(utc_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return None
    
    def process_json_file(self, json_file):
        """Process a single JSON file and convert UTC dates."""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract movie name and posts
        for movie_name, movie_data in data.items():
            posts = movie_data.get('posts', [])
            
            for post in posts:
                # Clean/normalize selftext and title
                if 'selftext' in post:
                    post['selftext'] = self.clean_text(post.get('selftext', ''))
                else:
                    post['selftext'] = ""
                if 'title' in post:
                    post['title'] = self.clean_text(post['title'])
                
                # If there's no selftext, try to use the first comment as fallback
                if not post['selftext']:
                    first_comment_text = None
                    # Prefer top_comment if present
                    if post.get('top_comment') and post['top_comment'].get('content'):
                        first_comment_text = post['top_comment']['content']
                    
                    if first_comment_text:
                        cleaned = self.clean_text(first_comment_text)
                        post['selftext'] = f"Top comment (no text on this post): {cleaned}"
                        post['selftext_source'] = 'first_comment'
                    else:
                        post['selftext_source'] = 'none'
                
                # Convert UTC timestamps to readable dates
                if 'created_utc' in post and post['created_utc']:
                    post['created_date'] = self.convert_utc_to_datetime(post['created_utc'])
                
                # Convert top comment UTC if exists
                if 'top_comment' in post and post['top_comment']:
                    if 'created_utc' in post['top_comment'] and post['top_comment']['created_utc']:
                        post['top_comment']['created_date'] = self.convert_utc_to_datetime(post['top_comment']['created_utc'])
                    if 'content' in post['top_comment']:
                        post['top_comment']['content'] = self.clean_text(post['top_comment']['content'])
                
                # Add movie name to post
                post['movie_name'] = movie_name
                self.all_posts.append(post)
        
        # Save converted JSON back
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Converted: {json_file}")
    
    def process_all_files(self):
        """Process all JSON files in the directory."""
        json_files = list(Path(self.parsed_posts_dir).glob('*.json'))
        # Skip progress files
        json_files = [f for f in json_files if '_progress.json' not in f.name]
        print(f"Found {len(json_files)} JSON files")
        
        for json_file in json_files:
            self.process_json_file(json_file)
        
        print(f"\n✓ Processed {len(self.all_posts)} total posts")
    
    def export_to_excel(self):
        """Export all posts to CSV file."""
        if not self.all_posts:
            print("No posts to export!")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.all_posts)
        
        # Reorder columns for better readability
        cols = ['movie_name', 'title', 'score', 'upvote_ratio', 'num_comments', 
                'created_date', 'author', 'selftext']
        
        # Keep only columns that exist
        cols = [col for col in cols if col in df.columns]
        df = df[cols]
        
        # Save to CSV
        os.makedirs(os.path.dirname(self.output_excel), exist_ok=True)
        output_csv = self.output_excel.replace('.xlsx', '.csv')
        df.to_csv(output_csv, index=False, encoding='utf-8')
        
        print(f"\n✓ Exported to CSV: {output_csv}")
        print(f"  Total rows: {len(df)}")
        print(f"  Columns: {', '.join(cols)}")

def main():
    parsed_posts_dir = r'c:\Users\Default\Desktop\COMP370FinalProj\data\parsed_movie_posts'
    output_excel = r'c:\Users\Default\Desktop\COMP370FinalProj\data\all_movie_posts.xlsx'
    
    print("Starting UTC conversion and Excel export...")
    
    converter = UTCDateConverter(parsed_posts_dir, output_excel)
    converter.process_all_files()
    converter.export_to_excel()
    
    print("\n✅ All done!")

if __name__ == "__main__":
    main()