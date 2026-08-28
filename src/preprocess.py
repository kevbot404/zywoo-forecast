import pandas as pd

def preprocess_features(df):
    """
    Preprocess the dataset by removing unwanted features.
    Decisions made through looking at ./data/dataset_audit.ipynb.
    """

    columns_to_drop = [
        "event_name",
        "location_city",
        "date",
        "player_team",
        "opponent",
        "map",
        "kd",
        "plus_minus",
        "nox",
        "no",
        "co",
        "so2",
        "sunset",
        "sunrise",
        "location_openaq",
        "weather_code"
    ]

    df = df.drop(columns=columns_to_drop, errors="ignore")


    return df
