import pandas as pd

def extract_opencoding(input_csv, output_csv, fill_value="Empty"):
    df = pd.read_csv(input_csv)
    
    required_columns = ['No.', 'opencoding1']
    for col in required_columns:
        if col not in df.columns:
            print("Column no found")
            return
    
    result_df = df[required_columns].copy()
    result_df['opencoding1'] = result_df['opencoding1'].fillna(fill_value)
    
    result_df.to_csv(output_csv, index=False)
    
    # op_df = df[['opencoding1']].fillna(fill_value)
    # op_df.to_csv(output_csv, index=False)
     
if __name__ == "__main__":
    extract_opencoding("../../data/open_coding/last_200_opencoding1.csv", "../../data/open_coding/opencoding.csv")