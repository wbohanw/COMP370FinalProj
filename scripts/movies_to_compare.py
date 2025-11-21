import requests as req
import argparse
import os
import json

def main():
    print("movies-to-compare script running...")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-m","--main_movie_title",type = str, required = True, help = "The name of the movie we selected for its analysis")
    parser.add_argument("-n","--num_movies_to_compare",type = int, required = True, help = "The number of movies released in same date as main movie")
    
    args = parser.parse_args()
    main_movie_title = args.main_movie_title
    total_num_movies_to_compares = args.num_movies_to_compare
    
    print(f"you picked the following movie: {main_movie_title}, and we will compare it with {total_num_movies_to_compares} other movies.")
    
    check_cache("main_movie", main_movie_title)

    release_date = ""
    
    
def check_cache(type, title):
    BASE_URL = "https://www.rottentomatoes.com/m/"
    
    print(f"checking cache for: {title} at folder: {type}")
    if os.path.exists(f"cache/{type}/{title}.html"):
        with open(f"cache/{type}/{title}.html", "r", encoding="utf-8") as f:
            html_content = f
    else:
        res = req.get(BASE_URL+str(title))
        print(f"api call code: {res.status_code}")
        with open(f"cache/{type}/{title}.html", "w") as f:
            json.dump(res.text, f)
        
    
    
    
if __name__ == "__main__":
    main()