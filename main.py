import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ProbeRequest(BaseModel):
    media_url: str

@app.post("/api/duration")
def get_duration(req: ProbeRequest):
    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            req.media_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        return {
            "media_url": req.media_url,
            "duration_seconds": float(result.stdout.strip())
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"FFprobe error: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))