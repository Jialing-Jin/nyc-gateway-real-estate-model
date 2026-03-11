import pandas as pd

def get_rent_growth(csv_path):

    df = pd.read_csv(csv_path)

    nyc = df[df["Borough"].notna()]

    rents = nyc.iloc[:, -13:-1]

    avg_rent = rents.mean().mean()

    prev_rent = rents.iloc[:, 0].mean()

    growth = (avg_rent - prev_rent) / prev_rent

    return growth