from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    youtube_url = request.form['youtube_url']
    # Placeholder response for now
    return f"Processing: {youtube_url}"

if __name__ == '__main__':
    app.run(debug=True)
