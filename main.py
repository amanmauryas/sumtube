import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load API keys from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: GEMINI_API_KEY not found in environment variables!")

genai.configure(api_key=api_key)  # Configure Gemini API key

app = Flask(__name__)

# Function to extract video ID from YouTube URL
def get_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    elif "/embed/" in url:
        return url.split("/embed/")[-1].split("?")[0]
    return None

# Function to fetch transcript (fallback to available language if requested one isn't found)
def get_transcript(video_id, language="en"):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    except NoTranscriptFound:
        # Try fetching any available transcript if the requested language isn't available
        try:
            available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = available_transcripts.find_generated_transcript(['en']).fetch()
            return transcript
        except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript):
            return None
    except TranscriptsDisabled:
        return None

# Function to generate summary using Gemini AI
def generate_summary(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize the following text in bullet points:\n{text}")
        return response.text
    except Exception as e:
        return f"⚠️ Error generating summary: {str(e)}"

# Flask API to summarize YouTube video
@app.route("/summarize", methods=["GET"])
def summarize():
    video_url = request.args.get("url")
    language = request.args.get("lang", "en")  # Default language is English

    if not video_url:
        return jsonify({"error": "Missing YouTube video URL"}), 400

    video_id = get_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    # Fetch transcript
    transcript = get_transcript(video_id, language)
    if not transcript:
        return jsonify({"error": "No subtitles available for this video"}), 404

    text = " ".join([t['text'] for t in transcript])

    # Generate Summary
    summary = generate_summary(text)

    return jsonify({
        "summary": summary,
        "transcript": text
    })

# Run Flask app locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
