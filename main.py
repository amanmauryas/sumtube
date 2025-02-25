import google.generativeai as genai
import os
import matplotlib.pyplot as plt
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Use Gemini API key

# Function to extract video ID from URL
def get_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

# Step 1: Ask for YouTube video URL
video_url = input("Enter YouTube Video URL: ")
video_id = get_video_id(video_url)

if not video_id:
    print("Invalid YouTube URL!")
    exit()

# Step 2: Ask for summary language
language = input("Enter summary language (e.g., en for English, hi for Hindi): ")

# Step 3: Fetch transcript
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    text = " ".join([t['text'] for t in transcript])
except:
    print("No subtitles available for this video!")
    exit()

# Step 4: Generate Summary using Google Gemini API
def generate_summary(text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Summarize the following text in bullet points:\n{text}")
    return response.text

summary = generate_summary(text)

# Save summary and transcript to a text file
output_file = "summary_output.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("🔹 Summary:\n" + summary + "\n\n")
    f.write("🔹 Full Transcript:\n" + text)

print(f"✅ Summary and transcript saved to {output_file}!")

# Step 5: Generate Graph (Example: Word Frequency)
def generate_graph(text):
    words = text.split()
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    labels, values = zip(*top_words)

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color="skyblue")
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.title("Top 10 Word Frequencies in Transcript")
    plt.xticks(rotation=45)
    plt.show()

print("\n📊 Generating Graph...")
generate_graph(text)
print("✅ Graph generated!")
