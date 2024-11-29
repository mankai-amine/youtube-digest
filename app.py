from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable

app = Flask(__name__)

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    youtube_url = request.form['youtube_url']
    try:
        # Fetch captions
        captions = fetch_captions(youtube_url)

        # Display captions as plain text
        return render_template('result.html', captions=captions)
    except ValueError as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
