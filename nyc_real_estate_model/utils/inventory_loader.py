import pandas as pd

def get_latest_inventory(csv_path):

    df = pd.read_csv(csv_path)

    nyc = df[df["Borough"].notna()]

    latest_inventory = nyc.iloc[:, -1].sum()

    return latest_inventory