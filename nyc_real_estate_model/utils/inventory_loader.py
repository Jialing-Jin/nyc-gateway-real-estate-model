import pandas as pd

def get_latest_inventory(csv_path):
    df = pd.read_csv(csv_path)
    nyc_row = df[df["areaType"] == "city"]
    latest_inventory = int(nyc_row.iloc[0, -1])
    return latest_inventory
