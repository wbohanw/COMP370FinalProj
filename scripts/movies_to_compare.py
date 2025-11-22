import requests as req
import argparse
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

def main():
    print("movies-to-compare script running...")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-m","--main_movie_title",type = str, required = True, help = "The name of the movie we selected for its analysis")
    parser.add_argument("-n","--num_movies_to_compare",type = int, required = True, help = "The number of movies released in same date as main movie")
    
    args = parser.parse_args()
    main_movie_title = args.main_movie_title
    total_num_movies_to_compares = args.num_movies_to_compare
    
    print(f"you picked the following movie: {main_movie_title}, and we will compare it with {total_num_movies_to_compares} other movies.")
    
    #get url bases for when we make api calls
    base_url_main_movie, websites_base_for_other_movies = get_urls()
    
    #check in cache if html of the movie we picked alr exists
    main_movie_html = check_cache("main_movie", base_url_main_movie, main_movie_title)
    #get release date of the movie picked - used rotten tomatoes website to get date
    release_date = get_release_date(main_movie_html)
    print(f"main movie was released on: {release_date}")
    
    #get movies that were released around same time as main movie
    cur_month_str, next_month_str = get_release_date_range(release_date)
    print(f"we will look at movies released from {cur_month_str} to {next_month_str}")
    
    movie_names = get_movies_rotten_tomatoes(websites_base_for_other_movies[0], cur_month_str, next_month_str)
    #get_movies_netflix(websites_base_for_other_movies[1])

    with open("data/movie_names.json", 'w', encoding='utf-8') as f:
        json.dump(movie_names, f, ensure_ascii=False, indent=4)
            
    

def get_urls():
    website_urls_path = os.path.join("data", "website_urls.json")
    with open(website_urls_path, "r") as f:
        website_urls = json.load(f)
    base_url_main_movie = website_urls["rotten_tomato_base"]
    websites_base_for_other_movies = website_urls["websites_base_for_other_movies"]
    
    return base_url_main_movie, websites_base_for_other_movies

def check_cache(type, base_url, title):
    filename = title
    if title == "":
        filename = "default"
        
    print(f"checking cache for: {filename} at folder: {type}")
    if os.path.exists(f"cache/{type}/{filename}.html"):
        with open(f"cache/{type}/{filename}.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            return html_content
    else:
        res = req.get(base_url+str(title))
        print(base_url+str(filename))
        print(f"api call code: {res.status_code}")
        os.makedirs(f"cache/{type}", exist_ok=True)
        with open(f"cache/{type}/{filename}.html", "w") as f:
            html_content = res.text
            f.write(html_content)
            return html_content

def get_release_date(html_content):
    print("getting release date of main movie...")
    
    soup = BeautifulSoup(html_content, "html.parser")
    metadata = soup.find_all("rt-text", slot="metadataProp")
    month, year = metadata[1].get_text(strip=True).split()
    release_date = f"{year}-{MONTH_MAP[month]}"
    return release_date
    
def get_release_date_range(release_date):
    release_date_formatted = datetime.strptime(release_date, "%Y-%m")

    cur_month_str = release_date_formatted.strftime("%Y-%m-%d")

    next_month = release_date_formatted + relativedelta(months=1)
    next_month_str = next_month.strftime("%Y-%m-%d")

    return cur_month_str, next_month_str

def get_movies_rotten_tomatoes(base_url, cur_month_str, next_month_str):
    #the website is 2025 but divided by months
    start_date_obj = datetime.strptime(cur_month_str, "%Y-%m-%d")
    end_date_obj = datetime.strptime(next_month_str, "%Y-%m-%d")
    
    if end_date_obj.month == 12:
        stop_date_obj = end_date_obj.replace(year=end_date_obj.year + 1, month=1)
    else:
        stop_date_obj = end_date_obj.replace(month=end_date_obj.month + 1)
    
    start_month_header = start_date_obj.strftime("%B").upper()
    stop_month_header = stop_date_obj.strftime("%B").upper()

    #get the rotten tomato html
    movies_rot_tom_page = check_cache("other_movies", base_url,"")
    soup = BeautifulSoup(movies_rot_tom_page, "html.parser")
    
    #month has a h2 tag
    start_node = soup.find(lambda tag: tag.name == "h2" and start_month_header in tag.get_text().upper())
    
    movie_names = []
    for sibling in start_node.find_next_siblings():
        
        if sibling.name == "h2":
            if stop_month_header in sibling.get_text().upper():
                break
            continue

        #get movie details
        movie_wrappers = sibling.find_all("p", class_="apple-news-link-wrap")
        
        for wrap in movie_wrappers:
            #movie title
            title = wrap.find("a", class_="title")
            if not title:
                continue
            
            movie_name = title.get_text(strip=True)

            #verify is movie year is 2025 and not a re-released 2024 in 2025 movie
            year_span = wrap.find("span", class_="year")
            if not year_span or "(2025)" not in year_span.get_text():
                continue

            if movie_name not in movie_names:
                movie_names.append(movie_name)

    return movie_names
    
    
def get_movies_netflix(base_url):
    #the website is summer 2025 so just loop
    pass
    
if __name__ == "__main__":
    main()