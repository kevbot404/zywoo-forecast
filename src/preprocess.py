def preprocess_features(df):
    """
    Preprocess the dataset by removing unwanted features.
    Decisions made through looking at ./data/dataset_audit.ipynb.
    """

    columns_to_drop = [
        "nox",
        "no",
        "co",
        "so2",
        "sunset",
        "sunrise",
        "player_team",
        "event_name",
        "location_city",
        "opponent",
        "location_openaq",
        "weather_code"
    ]

    df = df.drop(columns=columns_to_drop, errors="ignore")

    return df
