import pandas as pd
from file_paths import modified_file_path
all_stock_df = pd.read_csv(modified_file_path)
all_stock_df["Date"] = pd.to_datetime(all_stock_df["Date"])
industries = {}
for industry_name in list(all_stock_df.Industry.unique()):
    industries[industry_name] = list(
        all_stock_df.loc[all_stock_df.Industry == industry_name, "Symbol"].unique())
