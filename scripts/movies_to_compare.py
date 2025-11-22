import requests as req
import argparse
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter

MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

def main():
    print("movies-to-compare script running...")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-m","--main_movie_title",type = str, required = True, help = "The name of the movie we selected for its analysis")
    parser.add_argument("-n","--num_movies_to_compare",type = int, required = True, help = "The number of movies released in same date as main movie you want")
    
    args = parser.parse_args()
    main_movie_title = args.main_movie_title
    main_movie_title_slug = main_movie_title.replace(' ', '_')
    total_num_movies_to_compares = args.num_movies_to_compare
    
    print(f"you picked the following movie: {main_movie_title}, and we will compare it with {total_num_movies_to_compares} other movies.")
    
    #get url bases for when we make api calls
    base_url_main_movie, websites_base_for_other_movies = get_urls()
    
    #check in cache if html of the movie we picked alr exists
    main_movie_html = check_cache("main_movie", base_url_main_movie, main_movie_title_slug, main_movie_title_slug)
    #get release date of the movie picked - used rotten tomatoes website to get date
    release_date = get_release_date(main_movie_html)
    print(f"main movie was released on: {release_date}")
    
    #get movies that were released around same time as main movie
    cur_month, next_month = get_release_date_range(release_date)
    cur_month_str, next_month_str = format_dates(cur_month, next_month)
    print(f"we will look at movies released from {cur_month_str} to {next_month_str}")
    
    movie_names_rot_tom = get_movies_rotten_tomatoes(websites_base_for_other_movies[0], cur_month_str, next_month_str)
    movie_names_netflix = get_movies_netflix(websites_base_for_other_movies[1], cur_month_str, next_month_str)

    movie_names = movie_names_rot_tom + movie_names_netflix
    #write movies we want to compare to a file (including the main movie name we picked)
    save_movie_names_json(main_movie_title, movie_names, total_num_movies_to_compares)
            

def get_urls():
    website_urls_path = os.path.join("data", "website_urls.json")
    with open(website_urls_path, "r") as f:
        website_urls = json.load(f)
    base_url_main_movie = website_urls["rotten_tomato_base"]
    websites_base_for_other_movies = website_urls["websites_base_for_other_movies"]
    
    return base_url_main_movie, websites_base_for_other_movies

def check_cache(type, base_url, title, filename):
        
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

def get_movies_rotten_tomatoes(base_url, start_month_header, stop_month_header):
    #the website is 2025 but divided by months
    #get the rotten tomato html
    movies_rot_tom_page = check_cache("other_movies", base_url,"", "rotten_tomato_movies")
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
     
def get_movies_netflix(base_url, start_month_header, stop_month_header):
    #the website is summer 2025 so just loop
    movies_netlix_page = check_cache("other_movies", base_url,"", "netflix_movies")
    soup = BeautifulSoup(movies_netlix_page, "html.parser")
    
    #get month headers
    start_node = soup.find(lambda tag: tag.name in ['h2', 'h3'] and start_month_header in tag.get_text().upper())

    movie_names = []
    for sibling in start_node.find_next_siblings():
        
        if sibling.name in ['h2', 'h3'] and stop_month_header in sibling.get_text().upper():
            break

        title_tags = sibling.find_all(['strong', 'i'])
        
        for tag in title_tags:
            title = tag.get_text(strip=True)
            
            if len(title) > 5 and 'Netflix' not in title and 'Tudum' not in title and title not in movie_names:
                movie_names.append(title)

    return movie_names

def format_dates(cur_month_str, next_month_str):
    start_date_obj = datetime.strptime(cur_month_str, "%Y-%m-%d")
    end_date_obj = datetime.strptime(next_month_str, "%Y-%m-%d")
    
    if end_date_obj.month == 12:
        stop_date_obj = end_date_obj.replace(year=end_date_obj.year + 1, month=1)
    else:
        stop_date_obj = end_date_obj.replace(month=end_date_obj.month + 1)

    start_month_header = start_date_obj.strftime("%B").upper()
    stop_month_header = stop_date_obj.strftime("%B").upper()
    
    return start_month_header, stop_month_header

def save_movie_names_json(main_movie_title, movie_names, total_num_movies_to_compares):
    #we will write the movie anmes to a json but prioritize the ones that are common between the 
    #sources if we have more than the total_num_movies_to_compares that was inputted
    movie_counts = Counter(movie_names)
    
    unique_titles_set = set()
    unique_ordered_titles = []
    for title in movie_names:
        if title not in unique_titles_set:
            unique_ordered_titles.append(title)
            unique_titles_set.add(title)

    recurring_movies = []
    unique_movies = []
    
    for title in unique_ordered_titles:
        if movie_counts[title] > 1:
            recurring_movies.append(title)
        else:
            unique_movies.append(title)
            
    prioritized_list = recurring_movies + unique_movies
    final_movies_to_compare = prioritized_list[:total_num_movies_to_compares]
    
    if main_movie_title not in final_movies_to_compare:
        final_movies_to_compare.append(main_movie_title)
    
    with open("data/all_selected_movies.json", 'w', encoding='utf-8') as f:
        json.dump(final_movies_to_compare, f, ensure_ascii=False, indent=4)
        print(f"wrote {len(final_movies_to_compare)} movies to all_selected_movies.json")
        
if __name__ == "__main__":
    main()