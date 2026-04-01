FROM python:3.11-alpine

# Install ffprobe
RUN apk add --no-cache ffmpeg

# Install API dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Copy the script
COPY main.py /app/main.py
WORKDIR /app

# Run the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]