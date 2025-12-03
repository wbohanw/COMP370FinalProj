import pandas as pd

def add_no_col(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df.insert(0, "No.", range(1, len(df)+1))
    df.to_csv(output_csv, index=False)
    
if  __name__ == '__main__':
    add_no_col("../../data/all_movie_posts.csv", "../../data/open_coding/all_movie_posts_with_no.csv")