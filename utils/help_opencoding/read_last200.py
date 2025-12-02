import pandas as pd

def extract_last_200(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df.insert(0, "No.", range(1, len(df)+1))
    last_200 = df.tail(200)
    last_200.to_csv(output_csv, index=False)
    
if  __name__ == '__main__':
    extract_last_200("../../data/all_movie_posts.csv", "../../data/open_coding/all_movie_posts_last200_opencoding.csv")