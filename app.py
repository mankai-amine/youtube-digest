from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable
from openai import OpenAI
import os
from dotenv import load_dotenv



app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
client = OpenAI(api_key=os.getenv("API_KEY"))



def fetch_captions(video_url):
    try:
        # Extract video ID from URL
        if 'v=' in video_url:
            video_id = video_url.split('v=')[-1]
        elif 'youtu.be' in video_url:
            video_id = video_url.split('/')[-1]
        else:
            return "Invalid YouTube URL"

        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine transcript into a single string
        captions = " ".join([item['text'] for item in transcript])
        return captions
    except TranscriptsDisabled:
        raise ValueError("This video does not have captions enabled.")
    except VideoUnavailable:
        raise ValueError("This video is unavailable.")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")



def summarize_text(text):
    try:
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional summarizer. Create a concise, clear summary that captures the key points."},
                {"role": "user", "content": f"Summarize this text: {text}"}
            ],
            max_tokens=300
        )
        # Extract the summary from the response
        summary = response.choices[0].message.content.strip()        
        return summary
    except Exception as e:
        return f"An error occurred: {e}"  

 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    youtube_url = request.form['youtube_url']
    try:
        # Fetch captions
        captions = fetch_captions(youtube_url)

        # Summarize the captions
        summarized_text = summarize_text(captions)

        # Display the summarized text
        return render_template('result.html', captions=captions, summary = summarized_text)
    except ValueError as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)