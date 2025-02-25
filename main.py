import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load API keys from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Use Gemini API key

app = Flask(__name__)

# Function to extract video ID from URL
def get_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

# Generate summary using Google Gemini API
def generate_summary(text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Summarize the following text in bullet points:\n{text}")
    return response.text

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
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        text = " ".join([t['text'] for t in transcript])
    except:
        return jsonify({"error": "No subtitles available for this video"}), 404

    # Generate Summary
    summary = generate_summary(text)

    return jsonify({
        "summary": summary,
        "transcript": text
    })

# Run Flask app locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
