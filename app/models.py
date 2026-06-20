from . import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploads = db.relationship('UploadSession', backref='user', lazy=True)


class UploadSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_name = db.Column(db.String(128), nullable=True)
    dataset_summary = db.Column(db.JSON, nullable=True)
    cleaned_summary = db.Column(db.JSON, nullable=True)
    model_results = db.Column(db.JSON, nullable=True)
