import subprocess
import base64
import tempfile
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ProbeRequest(BaseModel):
    # Expecting the raw base64 string in the JSON payload
    base64_data: str

@app.post("/api/duration")
def get_duration(req: ProbeRequest):
    # 1. Decode the Base64 string into raw bytes
    try:
        media_bytes = base64.b64decode(req.base64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 string provided.")

    # 2. Write the bytes to a secure temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(media_bytes)
        temp_file_path = temp_file.name

    # 3. Run ffprobe against the temporary file
    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            temp_file_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        return {
            "duration_seconds": float(result.stdout.strip())
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"FFprobe error: {e.stderr}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Could not extract duration. Is the file a valid media format?")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 4. CRITICAL: Always delete the temp file immediately after, even if ffprobe fails
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)