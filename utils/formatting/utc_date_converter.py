import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

class UTCDateConverter:
    def __init__(self, parsed_posts_dir: str, output_excel: str):
        self.parsed_posts_dir = parsed_posts_dir
        self.output_excel = output_excel
        self.all_posts = []
    
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
                # Convert UTC timestamps to readable dates
                if 'created_utc' in post and post['created_utc']:
                    post['created_date'] = self.convert_utc_to_datetime(post['created_utc'])
                
                # Convert top comment UTC if exists
                if 'top_comment' in post and post['top_comment']:
                    if 'created_utc' in post['top_comment'] and post['top_comment']['created_utc']:
                        post['top_comment']['created_date'] = self.convert_utc_to_datetime(post['top_comment']['created_utc'])
                
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
        
        # Add top comment columns if they exist
        if 'top_comment' in df.columns:
            cols.extend(['top_comment'])
        
        # Keep only columns that exist
        cols = [col for col in cols if col in df.columns]
        df = df[cols]
        
        # Save to CSV instead
        os.makedirs(os.path.dirname(self.output_excel), exist_ok=True)
        output_csv = self.output_excel.replace('.xlsx', '.csv')
        df.to_csv(output_csv, index=False)
        
        print(f"\n✓ Exported to CSV: {output_csv}")
        print(f"  Total rows: {len(df)}")

def main():
    parsed_posts_dir = '/Users/eloisefreydier/Desktop/comp370 final project/COMP370FinalProj/data/parsed_movie_posts'
    output_excel = '/Users/eloisefreydier/Desktop/comp370 final project/COMP370FinalProj/data/all_movie_posts.xlsx'
    
    print("Starting UTC conversion and Excel export...")
    
    converter = UTCDateConverter(parsed_posts_dir, output_excel)
    converter.process_all_files()
    converter.export_to_excel()
    
    print("\n✅ All done!")

if __name__ == "__main__":
    main()