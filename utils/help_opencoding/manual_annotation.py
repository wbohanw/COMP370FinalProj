import pandas as pd

def add_No(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df.insert(0, "No.", range(1, len(df)+1))
    
    csv_opencoding_final = pd.read_csv("../../data/open_coding/opencoding3.csv")
    merged = pd.merge(df, csv_opencoding_final, on="No.", how="left")
    merged = merged.rename(columns={"opencoding3": "topics"})
    merged.to_csv(output_csv, index=False)
    
if  __name__ == '__main__':
    add_No("../../data/all_movie_posts.csv", "../../data/open_coding/manual_annotation_all_movie_posts.csv")