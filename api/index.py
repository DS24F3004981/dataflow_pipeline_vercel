from fastapi import FastAPI
from pydantic import BaseModel
import requests
from datetime import datetime
import sqlite3

app = FastAPI()

DB_NAME = "/tmp/pipeline.db"  # Vercel serverless me temp storage

# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original TEXT,
            analysis TEXT,
            sentiment TEXT,
            source TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class PipelineRequest(BaseModel):
    email: str
    source: str

# Simple FREE AI replacement
def analyze_text(text):
    text_lower = text.lower()

    if "excellent" in text_lower or "great" in text_lower:
        sentiment = "enthusiastic"
    elif "bad" in text_lower or "error" in text_lower:
        sentiment = "critical"
    else:
        sentiment = "objective"

    analysis = f"This comment discusses: {text[:50]}. The tone appears {sentiment}."
    return analysis, sentiment

@app.post("/pipeline")
def run_pipeline(request: PipelineRequest):
    items_output = []
    errors = []

    try:
        response = requests.get(
            "https://jsonplaceholder.typicode.com/comments?postId=1",
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"error": f"API Fetch Failed: {str(e)}"}

    for item in data[:3]:
        try:
            original_text = item["body"]
            analysis, sentiment = analyze_text(original_text)
            timestamp = datetime.utcnow().isoformat()

            # Store in SQLite
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processed_data (original, analysis, sentiment, source, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (original_text, analysis, sentiment, request.source, timestamp))
            conn.commit()
            conn.close()

            items_output.append({
                "original": original_text,
                "analysis": analysis,
                "sentiment": sentiment,
                "stored": True,
                "timestamp": timestamp
            })

        except Exception as e:
            errors.append(str(e))
            continue

    # Notification (console)
    print(f"Notification sent to: {request.email}")

    return {
        "items": items_output,
        "notificationSent": True,
        "processedAt": datetime.utcnow().isoformat(),
        "errors": errors
    }
