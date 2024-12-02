from . import db  # Import db object from app.py 

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False)