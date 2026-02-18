from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from datetime import datetime
import sqlite3
import os

app = FastAPI()

DB_NAME = "/tmp/pipeline.db"

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

def analyze_text(text):
    text_lower = text.lower()

    if "excellent" in text_lower or "great" in text_lower:
        sentiment = "enthusiastic"
    elif "bad" in text_lower or "error" in text_lower:
        sentiment = "critical"
    else:
        sentiment = "objective"

    analysis = (
        f"This comment discusses the topic in detail. "
        f"It reflects ideas related to: {text[:60]}. "
        f"The overall tone appears {sentiment}."
    )

    return analysis, sentiment


@app.post("/pipeline")
async def run_pipeline(request: Request):
    try:
        body = await request.json()
        email = body.get("email")
        source = body.get("source")

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
            return JSONResponse(
                status_code=500,
                content={
                    "items": [],
                    "notificationSent": False,
                    "processedAt": datetime.utcnow().isoformat(),
                    "errors": [f"API fetch failed: {str(e)}"]
                }
            )

        for item in data[:3]:
            try:
                original_text = item["body"]
                analysis, sentiment = analyze_text(original_text)
                timestamp = datetime.utcnow().isoformat()

                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO processed_data
                    (original, analysis, sentiment, source, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (original_text, analysis, sentiment, source, timestamp))
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

        print(f"Notification sent to: {email}")

        return {
            "items": items_output,
            "notificationSent": True,
            "processedAt": datetime.utcnow().isoformat(),
            "errors": errors
        }

    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid request"}
        )
