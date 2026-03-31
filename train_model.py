import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("user_logs.csv")

features = [
    "login_hour", "files_accessed", "emails_sent",
    "session_duration_min", "failed_logins",
    "vpn_usage", "data_uploaded_mb"
]

X = df[features]
y = df["is_anomaly"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("🔄 Training Isolation Forest...")
iso_forest = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42,
    max_samples='auto'
)
iso_forest.fit(X_scaled)

df["anomaly_score"] = iso_forest.decision_function(X_scaled)
df["predicted_anomaly"] = (iso_forest.predict(X_scaled) == -1).astype(int)

scores = df["anomaly_score"]
df["risk_score"] = 100 * (1 - (scores - scores.min()) / (scores.max() - scores.min()))

print("\n📊 Model Evaluation:")
print(classification_report(y, df["predicted_anomaly"], target_names=["Normal", "Anomaly"]))

cm = confusion_matrix(y, df["predicted_anomaly"])
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Reds',
            xticklabels=["Normal", "Anomaly"],
            yticklabels=["Normal", "Anomaly"])
plt.title("ThreatMind - Confusion Matrix")
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
print("✅ Confusion matrix saved")

print("\n🔍 Feature Importance (Anomaly Score Correlation):")
for f in features:
    corr = abs(np.corrcoef(X[f], df["risk_score"])[0, 1])
    bar = "█" * int(corr * 40)
    print(f"  {f:<25} {bar} {corr:.3f}")

joblib.dump(iso_forest, "threatmind_model.pkl")
joblib.dump(scaler, "scaler.pkl")
df.to_csv("results.csv", index=False)
print("\n✅ Model saved as threatmind_model.pkl")
