from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable
from openai import OpenAI
import os
from dotenv import load_dotenv
#from flask_sqlalchemy import SQLAlchemy
from database import db
from models import Favorite



# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set your OpenAI API key
client = OpenAI(api_key=os.getenv("API_KEY"))

# MySQL configuration
#app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('JAWSDB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()



def fetch_captions(video_url):
    try:
        if 'v=' in video_url:
            video_id = video_url.split('v=')[1].split('&')[0]
        elif 'youtu.be' in video_url:
            video_id = video_url.split('/')[-1].split('&')[0]

        print(f"Video ID: {video_id}")
        
        # Get list of available transcripts
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print("Available transcripts:", transcript_list.get_available_transcripts())
        except Exception as e:
            print(f"Error listing transcripts: {type(e).__name__}: {str(e)}")

        # Original code continues...
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])

    except Exception as e:
        print(f"Final error: {type(e).__name__}: {str(e)}")
        raise



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

@app.route('/summary', methods=['POST'])
def summarize():
    youtube_url = request.form['youtube_url']
    try:
        # Fetch captions
        captions = fetch_captions(youtube_url)

        # Summarize the captions
        summarized_text = summarize_text(captions)

        # Display the summarized text
        return render_template('result.html', captions=captions, summary = summarized_text, video_url= youtube_url )
    except ValueError as e:
        return f"An error occurred: {e}"

@app.route('/save-video', methods=['POST'])
def save_video():
    data = request.json
    video_url = data.get('video_url')
    summary = data.get('summary')

    if not video_url or not summary:
        return jsonify({"error": "Video URL and summary are required"}), 400

    # Add to database
    new_favorite = Favorite(video_url=video_url, summary=summary)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Video saved successfully"}), 200

@app.route('/favorites')
def favorites():
    favorites = Favorite.query.all()  
    return render_template('favorites.html', favorites=favorites)

@app.route('/delete/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Favorite.query.get(video_id)
    if video:
        db.session.delete(video)
        db.session.commit()
        return jsonify({"message": "Video deleted successfully"}), 200
    else:
        return jsonify({"error": "Video not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)