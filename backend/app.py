from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import random
from sqlalchemy import UniqueConstraint
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.abspath('database/sat_words.db')}"
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Change this for production security
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)  # Allows React to talk to Flask

# Database models
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), unique=True, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    synonym1 = db.Column(db.Text, nullable=False)
    synonym2 = db.Column(db.Text, nullable=False)
    sentence1 = db.Column(db.Text, nullable=False)
    sentence2 = db.Column(db.Text, nullable=False)
    frequency = db.Column(db.Integer, nullable=False)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('dictionary.id'), nullable=False)
    n = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    EF = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'word_id', name='uix_user_word'),  # Ensures unique pair of user_id and word_id
    )

# Create tables (run once)
with app.app_context():
    db.create_all()

# User registration
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token}), 200

# Get a random word (protected)
@app.route("/api/word", methods=["GET"])
@jwt_required()
def get_word():
    user_id = get_jwt_identity()
    
    # Fetch words the user hasn't reviewed yet
    reviewed_words = db.session.query(UserProgress.word_id).filter_by(user_id=user_id).subquery()
    word = Word.query.filter(~Word.id.in_(reviewed_words)).order_by(db.func.random()).first()

    if word:
        return jsonify({"word": word.word})
    else:
        return jsonify({"message": "No new words available"}), 404

# Get word definition (protected)
@app.route("/api/definition/<word>", methods=["GET"])
@jwt_required()
def get_definition(word):
    word_entry = Word.query.filter_by(word=word).first()
    if word_entry:
        return jsonify({"definition": word_entry.definition})
    return jsonify({"message": "Word not found"}), 404

# Submit recall rating (protected)
@app.route("/api/rate", methods=["POST"])
@jwt_required()
def submit_rating():
    data = request.json
    user_id = get_jwt_identity()
    word = data.get("word")
    rating = data.get("rating")

    word_entry = Word.query.filter_by(word=word).first()
    if not word_entry:
        return jsonify({"message": "Word not found"}), 404

    user_progress = UserProgress.query.filter_by(user_id=user_id, word_id=word_entry.id).first()
    if user_progress:
        user_progress.recall_score = rating  # Update existing rating
    else:
        new_progress = UserProgress(user_id=user_id, word_id=word_entry.id, recall_score=rating)
        db.session.add(new_progress)

    db.session.commit()
    return jsonify({"message": "Rating submitted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
