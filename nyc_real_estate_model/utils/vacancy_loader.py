import pandas as pd

def get_latest_vacancy(csv_path):

    df = pd.read_csv(csv_path)

    latest_vacancy = df.iloc[-1]["NYHVAC"] / 100

    return latest_vacancy