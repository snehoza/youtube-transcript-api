import os
import re

from fastapi import FastAPI, HTTPException
from youtube_transcript_api import (
    AgeRestricted,
    CouldNotRetrieveTranscript,
    FailedToCreateConsentCookie,
    InvalidVideoId,
    IpBlocked,
    NoTranscriptFound,
    PoTokenRequired,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    VideoUnplayable,
    YouTubeDataUnparsable,
    YouTubeRequestFailed,
    YouTubeTranscriptApi,
)
import uvicorn

app = FastAPI()
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def _fetch_transcript(video_id: str):
    # Support both modern (instance fetch) and legacy (class get_transcript) APIs.
    if hasattr(YouTubeTranscriptApi, "get_transcript"):
        return YouTubeTranscriptApi.get_transcript(video_id)
    return YouTubeTranscriptApi().fetch(video_id)


def _flatten_transcript(transcript_items) -> str:
    parts = []
    for item in transcript_items:
        if isinstance(item, dict):
            text = item.get("text", "").strip()
        else:
            text = str(getattr(item, "text", "")).strip()
        if text:
            parts.append(text)
    return " ".join(parts)


def _http_exception_for_transcript_error(exc: Exception) -> HTTPException:
    if isinstance(exc, InvalidVideoId):
        return HTTPException(
            status_code=400,
            detail="Invalid video_id. Use the 11-character YouTube video ID.",
        )

    if isinstance(exc, (VideoUnavailable, NoTranscriptFound)):
        return HTTPException(status_code=404, detail="Transcript not found for this video.")

    if isinstance(exc, (TranscriptsDisabled, AgeRestricted, VideoUnplayable)):
        return HTTPException(status_code=403, detail="Transcript is unavailable for this video.")

    if isinstance(exc, (RequestBlocked, IpBlocked)):
        return HTTPException(
            status_code=429,
            detail="YouTube is rate-limiting transcript requests from this IP. Try again later.",
        )

    if isinstance(
        exc,
        (
            YouTubeRequestFailed,
            FailedToCreateConsentCookie,
            PoTokenRequired,
            YouTubeDataUnparsable,
            CouldNotRetrieveTranscript,
        ),
    ):
        return HTTPException(
            status_code=502,
            detail="Unable to retrieve transcript from YouTube right now.",
        )

    return HTTPException(status_code=500, detail="Internal server error.")

@app.get("/")
def read_root():
    return {"status": "YouTube Transcript API is running"}

@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):
    video_id = video_id.strip()
    if not VIDEO_ID_PATTERN.fullmatch(video_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid video_id format. Expected 11 characters [A-Za-z0-9_-].",
        )

    try:
        # Fetch the transcript
        transcript_list = _fetch_transcript(video_id)
        
        # Flatten the array of dictionaries into one long string
        full_text = _flatten_transcript(transcript_list)
        
        return {
            "success": True, 
            "video_id": video_id, 
            "transcript": full_text
        }
    except Exception as e:
        raise _http_exception_for_transcript_error(e)

# This allows it to run on Render's assigned ports
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
