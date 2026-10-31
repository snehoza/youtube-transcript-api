# YouTube Transcript API

A lightweight FastAPI service that fetches the transcript text for a YouTube video and returns it as a single string via a simple HTTP endpoint.

## Overview

This project wraps the `youtube-transcript-api` library and exposes it through a REST API. It validates the YouTube video ID, fetches the transcript, combines all transcript segments into one readable string, and returns JSON responses with appropriate HTTP status codes for common failures.

## Features

- Fetch transcript text for any valid 11-character YouTube video ID
- Flat response format for easy downstream usage
- FastAPI-based API with clear error handling
- Works with standard YouTube transcript retrieval errors mapped to HTTP status codes
- Ready for deployment on platforms like Render

## Tech Stack

- Python
- FastAPI
- Uvicorn
- youtube-transcript-api

## Local Setup

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 10000
```

The app will be available at:

- `http://localhost:10000/`
- `http://localhost:10000/transcript/{video_id}`

## API Endpoints

### GET /

Health check endpoint.

Example response:

```json
{
  "status": "YouTube Transcript API is running"
}
```

### GET /transcript/{video_id}

Fetches the transcript for a YouTube video.

Example:

```bash
curl "http://localhost:10000/transcript/dQw4w9WgXcQ"
```

Example response:

```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "transcript": "Hello and welcome to this video. ..."
}
```

## Notes

- `video_id` must be an 11-character YouTube ID matching the pattern `[A-Za-z0-9_-]`.
- If the transcript is unavailable, blocked, or invalid, the API returns an HTTP error response with a detailed message.

## Deployment

This repository includes a `Procfile` for deployment on Render or similar platforms:

```procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

## License

This project does not currently include a license file. Add one if you plan to publish or share it publicly.
