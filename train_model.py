import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_and_save_model(csv_path, model_path="phishing_model_30.pkl"):
    # 1. Load dataset
    df = pd.read_csv(csv_path)
    print("✅ Dataset loaded successfully!")
    print("📌 Columns available:", df.columns.tolist())

    # 2. Clean dataset (convert b'1' → 1, b'-1' → -1, etc.)
    df = df.applymap(
        lambda x: int(str(x).replace("b'", "").replace("'", "")) if isinstance(x, str) else x
    )

    # 3. Target column
    target_col = "Result"
    X = df.drop(columns=[target_col])   # 30 features
    y = df[target_col]                  # labels

    print("🔢 Feature count:", X.shape[1])  # should print 30

    # 4. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 5. Train model
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 6. Evaluate model
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Model trained successfully with accuracy: {acc:.4f}")
    print("\n📊 Classification Report:\n", classification_report(y_test, y_pred))

    # 7. Save model
    joblib.dump(model, model_path)
    print(f"💾 Model saved to {os.path.abspath(model_path)}")

if __name__ == "__main__":
    train_and_save_model(
        "D://Capstone_Project//Phishing 2.0//phishing.csv",
        model_path="D://Capstone_Project//Phishing 2.0//models_store//phishing_model_30.pkl"
    )
