import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

def generate_user_logs(n_users=50, n_days=30):
    records = []
    users = [f"user_{i:03d}" for i in range(n_users)]
    departments = ["HR", "Finance", "Engineering", "Sales", "IT"]
    
    for user in users:
        dept = random.choice(departments)
        avg_login_hour = random.randint(7, 10)
        avg_files = random.randint(5, 20)
        avg_emails = random.randint(10, 40)
        avg_duration = random.randint(300, 480)

        for day in range(n_days):
            date = datetime.now() - timedelta(days=n_days - day)
            is_anomaly = (user in users[:5]) and (day >= n_days - 5)

            login_hour = random.randint(0, 4) if is_anomaly else int(np.random.normal(avg_login_hour, 1))
            files_accessed = random.randint(80, 150) if is_anomaly else int(np.random.normal(avg_files, 3))
            emails_sent = random.randint(60, 100) if is_anomaly else int(np.random.normal(avg_emails, 5))
            session_duration = random.randint(10, 60) if is_anomaly else int(np.random.normal(avg_duration, 30))
            failed_logins = random.randint(5, 15) if is_anomaly else random.randint(0, 2)
            vpn_usage = 1 if is_anomaly else random.choice([0, 0, 0, 1])
            data_uploaded_mb = random.randint(500, 2000) if is_anomaly else random.randint(1, 50)

            records.append({
                "user_id": user,
                "department": dept,
                "date": date.strftime("%Y-%m-%d"),
                "login_hour": max(0, min(23, login_hour)),
                "files_accessed": max(0, files_accessed),
                "emails_sent": max(0, emails_sent),
                "session_duration_min": max(1, session_duration),
                "failed_logins": max(0, failed_logins),
                "vpn_usage": vpn_usage,
                "data_uploaded_mb": max(0, data_uploaded_mb),
                "is_anomaly": int(is_anomaly)
            })

    df = pd.DataFrame(records)
    df.to_csv("user_logs.csv", index=False)
    print(f"✅ Generated {len(df)} records for {n_users} users over {n_days} days")
    return df

if __name__ == "__main__":
    generate_user_logs()
