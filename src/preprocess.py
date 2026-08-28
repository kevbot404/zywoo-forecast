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
        "kd",
        "plus_minus",
        "nox",
        "no",
        "sunset",
        "sunrise",
        "location_openaq",
        "weather_code"
    ]

    df = df.drop(columns=columns_to_drop, errors="ignore")

    # Convert categorical map into numerical features
    df = pd.get_dummies(df, columns=["map"], dtype=int)

    return df
