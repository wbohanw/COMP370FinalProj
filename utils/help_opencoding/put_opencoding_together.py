import pandas as pd

csv_opencoding1 = pd.read_csv("../../data/open_coding/opencoding1.csv")
csv_opencoding2 = pd.read_csv("../../data/open_coding/opencoding2.csv")
csv_opencoding3 = pd.read_csv("../../data/open_coding/opencoding3.csv")

merged = pd.merge(csv_opencoding1, csv_opencoding2, on="No.", how="left")
merged = pd.merge(merged, csv_opencoding3, on="No.", how="left")
merged.to_csv("../../data/open_coding/opencoding_process.csv", index=False)