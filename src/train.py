import os

import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

from preprocess import preprocess_features


DATA_PATH = "./data/dataset.csv"
ONNX_PATH = "./app/model/rating_model.onnx"
TARGET = "rating"

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")

df = df.dropna(subset=[TARGET])

y = df[TARGET]

X = preprocess_features(df)

# Make absolutely sure the target isn't in X
X = X.drop(columns=[TARGET], errors="ignore")


print(f"\nFeatures: {X.shape[1]}")
print(f"Samples:  {X.shape[0]}")

print("\nFeatures used:")
print(X.columns.tolist())


# replace missing numerical values with the median
X = X.fillna(X.median(numeric_only=True))

# check if anything is still missing
remaining_missing = X.isna().sum().sum()

if remaining_missing > 0:
    print(f"\nWarning: {remaining_missing} missing values remain.")


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print(f"\nTraining samples: {len(X_train)}")
print(f"Test samples:     {len(X_test)}")


model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("\n" + "=" * 50)
print("MODEL RESULTS")
print("=" * 50)

print(f"MAE:  {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²:   {r2:.4f}")

feature_importance = (
    pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_
    })
    .sort_values("importance", ascending=False)
)

print("\n" + "=" * 50)
print("FEATURE IMPORTANCE")
print("=" * 50)

print(feature_importance.to_string(index=False))


results = pd.DataFrame({
    "actual": y_test.values,
    "predicted": y_pred
})

print("\n" + "=" * 50)
print("EXAMPLE PREDICTIONS")
print("=" * 50)

print(results.head(10).to_string(index=False))

print("\n" + "=" * 50)
print("EXPORTING ONNX MODEL")
print("=" * 50)

# ONNX expects float32 input
X_train_float = X_train.astype("float32")

initial_type = [
    (
        "float_input",
        FloatTensorType([None, X_train_float.shape[1]])
    )
]

onnx_model = convert_sklearn(
    model,
    initial_types=initial_type,
    target_opset=15
)

os.makedirs(os.path.dirname(ONNX_PATH), exist_ok=True)

with open(ONNX_PATH, "wb") as f:
    f.write(onnx_model.SerializeToString())

print(f"ONNX model saved to: {ONNX_PATH}")