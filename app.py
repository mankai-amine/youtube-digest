from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable
# from sumy.parsers.plaintext import PlaintextParser
# from sumy.summarizers.lsa import LsaSummarizer
# from sumy.nlp.tokenizers import Tokenizer
# from nltk.tokenize import word_tokenize
# from sumy.summarizers.lex_rank import LexRankSummarizer
#from transformers import pipeline
#import requests
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


# def summarize_text(text):

#     # Create the parser from the provided text
#     parser = PlaintextParser.from_string(text, Tokenizer('english'))
#     summarizer = LsaSummarizer()
#     summary = summarizer(parser.document, 10)

#     # Combine the sentences in the summary into a single string
#     summary_text = ". ".join([str(sentence) for sentence in summary])

#     return summary_text



# Load the summarizer pipeline with BART model
#summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# def summarize_text(text):
#     try:
#         # Call the summarizer
#         summary = summarizer(text, max_length=250, min_length=150, do_sample=False)
        
#         # Ensure the summarizer returned a valid response
#         if not summary or len(summary) == 0:
#             raise ValueError("The summarizer returned an empty response.")
        
#         # Return the summarized text
#         return summary[0]['summary_text']
#     except IndexError:
#         return "No summary could be generated. The model returned no output."
#     except Exception as e:
#         return f"An error occurred: {e}"




# # Your Hugging Face API token
# API_TOKEN = ******

# # The URL for the Hugging Face API summarization endpoint
# url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# # Set up the headers for authentication
# headers = {"Authorization": f"Bearer {API_TOKEN}"}

# def summarize_text(text):
#     # Call the Hugging Face API for summarization
#     response = requests.post(
#         url, 
#         headers=headers, 
#         json={"inputs": text, 
#               "parameters": {
#                   "max_length": 350,   # Maximum length of summary (tokens)
#                   "min_length": 250,    # Minimum length of summary (tokens)
#                   "do_sample": False   # Ensure deterministic results
#               }
#         }
#     )
    
#     # Check if the response is successful
#     if response.status_code == 200:
#         summary = response.json()
#         return summary[0]['summary_text']  
#     else:
#         return f"Error: {response.status_code} - {response.text}"