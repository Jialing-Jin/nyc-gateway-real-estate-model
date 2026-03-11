import pandas as pd

def get_latest_discount(csv_path):

    df = pd.read_csv(csv_path)

    nyc = df[df["Borough"].notna()]

    latest_discount = nyc.iloc[:, -1].mean()

    return latest_discount