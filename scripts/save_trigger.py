import requests
import os
from datetime import datetime

db_url = os.getenv("FIREBASE_DATABASE_URL", "").rstrip("/")
db_secret = os.getenv("FIREBASE_DB_SECRET", "")

if not db_url or not db_secret:
    print("Firebase env vars missing - skipping")
    exit(0)

r = requests.put(
    db_url + "/kaggle_trigger.json?auth=" + db_secret,
    json={"triggered_at": datetime.now().isoformat(), "status": "requested"},
    timeout=15
)
print("Trigger saved: " + str(r.status_code))
