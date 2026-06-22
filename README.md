# Dataflow Pipeline Vercel

A FastAPI-based data processing pipeline deployed on Vercel that fetches, analyzes, and stores textual data with sentiment analysis capabilities.

## Overview

This project implements a serverless data pipeline that:
- Fetches data from external APIs
- Performs sentiment analysis on text content
- Stores processed results in an SQLite database
- Exposes a POST endpoint for pipeline execution

## Features

- **Text Analysis**: Automatic sentiment classification (enthusiastic, critical, or objective)
- **Data Persistence**: SQLite database for storing processed records
- **API Integration**: Fetches data from JSONPlaceholder API
- **Error Handling**: Comprehensive error handling and reporting
- **Serverless Deployment**: Ready for Vercel deployment

## Tech Stack

- **FastAPI**: Python web framework for building APIs
- **SQLite**: Lightweight database for data storage
- **Requests**: HTTP client for external API calls
- **Vercel**: Serverless platform for deployment

## Project Structure

```
dataflow_pipeline_vercel/
├── api/
│   └── index.py          # Main FastAPI application
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel deployment configuration
├── pipeline.db          # SQLite database file
└── README.md            # This file
```

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/DS24F3004981/dataflow_pipeline_vercel.git
cd dataflow_pipeline_vercel
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running Locally

Start the development server:
```bash
uvicorn api.index:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoint

**POST** `/pipeline`

Process data through the pipeline.

**Request Body:**
```json
{
  "email": "user@example.com",
  "source": "data_source_identifier"
}
```

**Response:**
```json
{
  "items": [
    {
      "original": "Text content...",
      "analysis": "Detailed analysis...",
      "sentiment": "enthusiastic|critical|objective",
      "stored": true,
      "timestamp": "2026-02-18T14:30:25.123456"
    }
  ],
  "notificationSent": true,
  "processedAt": "2026-02-18T14:30:25.123456",
  "errors": []
}
```

## Database Schema

The pipeline stores processed data in the `processed_data` table:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| original | TEXT | Original text content |
| analysis | TEXT | Generated analysis |
| sentiment | TEXT | Sentiment classification |
| source | TEXT | Data source identifier |
| timestamp | TEXT | ISO format timestamp |

## Sentiment Analysis

The sentiment analysis uses keyword-based classification:
- **Enthusiastic**: Text contains "excellent" or "great"
- **Critical**: Text contains "bad" or "error"
- **Objective**: Default classification for other text

## Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

The application will be configured according to `vercel.json`:
- **Build Target**: `api/index.py`
- **Route**: `/pipeline` maps to the FastAPI application

## Requirements

- Python 3.7+
- FastAPI
- Requests
- SQLite3 (included with Python)

See `requirements.txt` for specific versions.

## Error Handling

The pipeline includes comprehensive error handling:
- Validates request format
- Handles external API failures with timeout protection (5 seconds)
- Catches and logs individual data processing errors
- Returns detailed error messages in the response

## Development

### Adding New Features

1. Modify the `analyze_text()` function to enhance sentiment analysis
2. Update the database schema in `init_db()` for new data fields
3. Add new routes to the FastAPI app

### Testing

You can test the endpoint using curl:
```bash
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","source":"test"}'
```

## License

This project is open source and available under the MIT License.

## Author

Created by DS24F3004981

## Notes

- The database file is created automatically on first run
- The pipeline fetches data from JSONPlaceholder API for demonstration
- Processing is limited to the first 3 items from the API response
- All timestamps are in UTC
