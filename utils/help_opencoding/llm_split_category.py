import os
import pandas as pd

def split_post_to_category(input_csv, output_dir):
    movie_posts_with_topics_df = pd.read_csv(input_csv)
    unique_topics = movie_posts_with_topics_df["topics"].unique()
    #movie_posts_with_topics_df = movie_posts_with_topics_df.dropna(subset=["topics"])
    find_empty_topics(input_csv)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for topic in unique_topics:
        safe_topic = "".join([c if c.isalnum() or c in "_-" else "_" for c in str(topic)])
        topic_df = movie_posts_with_topics_df[movie_posts_with_topics_df["topics"] == topic]
        output_path = os.path.join(output_dir, f"{safe_topic}.csv")
        topic_df.to_csv(output_path, index=False)
        

def find_empty_topics(input_csv):
    df = pd.read_csv(input_csv)
    
    empty_topics_df = df[df["topics"].isna() | (df["topics"].astype(str).str.strip() == "")]
    
    if not empty_topics_df.empty:
        print("Empty or NaN which No?: ")
        print(empty_topics_df["No."].tolist())
    else:
        print("No empty or NaN topics found")
        
if __name__ == "__main__":
    split_post_to_category("../../data/open_coding/manual_annotation_all_movie_posts.csv", "../../data/open_coding/llm/")