# Overview
An AI-powered web application that extracts and summarizes YouTube video content using transcripts.

## Key Features
- **YouTube Transcript Extraction**: Automatically pulls captions from any YouTube video with available transcripts
- **AI-Powered Summarization**: Leverages OpenAI's GPT-3.5 model to create clear summaries
- **Favorites Management**: Save, view, and delete your favorite video summaries

## Technologies
- **Backend**: Flask (Python), SQLAlchemy
- **Database**: MySQL
- **APIs**: 
  - YouTube Transcript API for caption extraction
  - OpenAI API for text summarization
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-digest.git
cd youtube-digest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
API_KEY=your_openai_api_key
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
```

4. Initialize the database:
```bash
flask db upgrade
```
