from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib

app = Flask(__name__)
CORS(app)

model = joblib.load("threatmind_model.pkl")
scaler = joblib.load("scaler.pkl")
df = pd.read_csv("results.csv")

FEATURES = [
    "login_hour", "files_accessed", "emails_sent",
    "session_duration_min", "failed_logins",
    "vpn_usage", "data_uploaded_mb"
]

@app.route("/api/summary", methods=["GET"])
def summary():
    total_users = df["user_id"].nunique()
    flagged_users = df[df["predicted_anomaly"] == 1]["user_id"].nunique()
    total_events = len(df)
    anomaly_events = int(df["predicted_anomaly"].sum())
    high_risk = df[df["risk_score"] >= 75]["user_id"].nunique()
    return jsonify({
        "total_users": int(total_users),
        "flagged_users": int(flagged_users),
        "total_events": int(total_events),
        "anomaly_events": anomaly_events,
        "high_risk_users": int(high_risk),
        "detection_rate": round(float(anomaly_events / total_events * 100), 2)
    })

@app.route("/api/users", methods=["GET"])
def get_users():
    user_summary = df.groupby("user_id").agg(
        department=("department", "first"),
        avg_risk_score=("risk_score", "mean"),
        max_risk_score=("risk_score", "max"),
        anomaly_count=("predicted_anomaly", "sum"),
        total_events=("predicted_anomaly", "count")
    ).reset_index()
    user_summary["threat_level"] = user_summary["max_risk_score"].apply(
        lambda x: "🔴 Critical" if x >= 80 else ("🟠 High" if x >= 60 else ("🟡 Medium" if x >= 40 else "🟢 Low"))
    )
    user_summary = user_summary.sort_values("max_risk_score", ascending=False)
    return jsonify(user_summary.round(2).to_dict(orient="records"))

@app.route("/api/user/<user_id>", methods=["GET"])
def get_user_detail(user_id):
    user_df = df[df["user_id"] == user_id].copy()
    if user_df.empty:
        return jsonify({"error": "User not found"}), 404
    timeline = user_df[["date", "risk_score", "predicted_anomaly",
                         "files_accessed", "emails_sent", "failed_logins",
                         "data_uploaded_mb", "login_hour"]].to_dict(orient="records")
    return jsonify({
        "user_id": user_id,
        "department": user_df["department"].iloc[0],
        "avg_risk": round(float(user_df["risk_score"].mean()), 2),
        "max_risk": round(float(user_df["risk_score"].max()), 2),
        "anomaly_days": int(user_df["predicted_anomaly"].sum()),
        "timeline": timeline
    })

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    anomalies = df[df["predicted_anomaly"] == 1].copy()
    anomalies = anomalies.sort_values("risk_score", ascending=False).head(20)
    alerts = []
    for _, row in anomalies.iterrows():
        reasons = []
        if row["login_hour"] < 5 or row["login_hour"] > 22:
            reasons.append("Unusual login time")
        if row["files_accessed"] > 50:
            reasons.append("Excessive file access")
        if row["failed_logins"] > 3:
            reasons.append("Multiple failed logins")
        if row["data_uploaded_mb"] > 200:
            reasons.append("Large data upload")
        if row["emails_sent"] > 50:
            reasons.append("Abnormal email activity")
        alerts.append({
            "user_id": row["user_id"],
            "department": row["department"],
            "date": row["date"],
            "risk_score": round(float(row["risk_score"]), 1),
            "reasons": reasons if reasons else ["Behavioral deviation detected"]
        })
    return jsonify(alerts)

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json
    try:
        input_data = np.array([[
            data["login_hour"], data["files_accessed"], data["emails_sent"],
            data["session_duration_min"], data["failed_logins"],
            data["vpn_usage"], data["data_uploaded_mb"]
        ]])
        scaled = scaler.transform(input_data)
        score = model.decision_function(scaled)[0]
        prediction = model.predict(scaled)[0]
        risk = round(float(100 * (1 - (score + 0.5))), 1)
        risk = max(0, min(100, risk))
        return jsonify({
            "is_threat": bool(prediction == -1),
            "risk_score": risk,
            "threat_level": "Critical" if risk >= 80 else ("High" if risk >= 60 else ("Medium" if risk >= 40 else "Low")),
            "message": "⚠️ Insider threat detected!" if prediction == -1 else "✅ Behavior appears normal"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/trend", methods=["GET"])
def trend():
    daily = df.groupby("date").agg(
        anomalies=("predicted_anomaly", "sum"),
        avg_risk=("risk_score", "mean"),
        total=("predicted_anomaly", "count")
    ).reset_index()
    return jsonify(daily.round(2).to_dict(orient="records"))

if __name__ == "__main__":
    print("🚀 ThreatMind API running at http://localhost:5000")
    app.run(debug=True, port=5000)
