import pandas as pd

def extract_first_417(output_csv):
    df = pd.read_csv(output_csv)
    # df["No."] = range(1, len(df) + 1)
    # first_418 = df.head(418)
    required_columns = ['No.']
    for col in required_columns:
        if col not in df.columns:
            no_col = pd.DataFrame({"No.": range(1, 417 + 1)})
            no_col.to_csv(output_csv, index=False)
            return
    
    print("No. not created as exist")
        
    
    
if  __name__ == '__main__':
    extract_first_417("../../data/open_coding/first400_manual_annotation.csv")