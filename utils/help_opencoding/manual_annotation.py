import pandas as pd

def put_opencoding_manual_annotation_together(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df.insert(0, "No.", range(1, len(df)+1))
    
    csv_opencoding_final = pd.read_csv("../../data/open_coding/opencoding3.csv")
    csv_manual_annotation_first416 = pd.read_csv("../../data/open_coding/first400_manual_annotation.csv")
    
    csv_opencoding_final = csv_opencoding_final.rename(columns={"opencoding3": "topics"})
    combined = pd.concat([csv_manual_annotation_first416, csv_opencoding_final], ignore_index=True)
    combined = combined.sort_values(by="No.").reset_index(drop=True)
    merged = pd.merge(df, combined, on="No.", how="left")
    merged.to_csv(output_csv, index=False)
    
if  __name__ == '__main__':
    put_opencoding_manual_annotation_together("../../data/all_movie_posts.csv", "../../data/open_coding/manual_annotation_all_movie_posts.csv")