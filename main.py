import google.generativeai as genai
import os
from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Use Gemini API key

# Initialize FastAPI
app = FastAPI()

# Function to extract video ID from URL
def get_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

# Define request model
class VideoRequest(BaseModel):
    video_url: str
    language: str = "en"  # Default to English

# Step 1: API Endpoint for YouTube Processing
@app.post("/process_video")
def process_video(data: VideoRequest):
    video_id = get_video_id(data.video_url)
    
    if not video_id:
        return {"error": "Invalid YouTube URL!"}

    # Step 2: Fetch transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[data.language])
        text = " ".join([t['text'] for t in transcript])
    except:
        return {"error": "No subtitles available for this video!"}

    # Step 3: Generate Summary using Google Gemini API
    def generate_summary(text):
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize the following text in bullet points:\n{text}")
        return response.text

    summary = generate_summary(text)

    # Step 4: Save summary and transcript to a text file
    output_file = "summary_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("🔹 Summary:\n" + summary + "\n\n")
        f.write("🔹 Full Transcript:\n" + text)

    return {
        "message": "✅ Summary and transcript saved!",
        "summary": summary,
        "output_file": output_file
    }

# Run the API (Render needs dynamic port)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
