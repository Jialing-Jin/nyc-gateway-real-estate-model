import pandas as pd

def get_latest_nyc_rent(csv_path):

    df = pd.read_csv(csv_path)

    nyc = df[df["Borough"].notna()]

    latest_rent = nyc.iloc[:, -1].mean()

    return latest_rent