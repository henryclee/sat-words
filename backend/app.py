from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import UniqueConstraint
import os
import datetime
from sm_2 import sm_2

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.abspath('database/sat_words.db')}"
app.config["JWT_VERIFY_SUB"]=False
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Change this for production security
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
# CORS(app)  # Allows React to talk to Flask
# CORS(app, supports_credentials=True, allow_headers=["Authorization", "Content-Type"])
# CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})  # Allow all origins for simplicity



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
# with app.app_context():
#     db.create_all()

# User registration
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if Users.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = Users(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# User login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = Users.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token}), 200

# Get a random word (protected)
@app.route("/api/word", methods=["GET"])
@jwt_required()
def get_word():
    user_id = get_jwt_identity()

    # First, get the next word from the database based on due dates
    next_word_query = db.session.query(
        UserProgress.word_id, UserProgress.due_date
        ).filter_by(user_id=user_id).order_by(
            UserProgress.due_date, db.func.random()
        ).first()
    
    if next_word_query:
        next_word_id, due_date = next_word_query
    else:
        next_word_id, due_date = None, None
    
    # If this word is not yet due, try to find a new word that hasn't been reviewed yet    
    if not next_word_query or datetime.datetime.strptime(due_date, "%Y-%m-%d").date() > datetime.date.today():
        reviewed_words = db.session.query(UserProgress.word_id).filter_by(user_id=user_id).subquery()
        new_word = Dictionary.query.filter(
            ~Dictionary.id.in_(reviewed_words)
            ).order_by(
                Dictionary.frequency, db.func.random()
            ).first().word
        if new_word:
            return jsonify({"word": new_word})

    next_word = Dictionary.query.get(next_word_id)
    return jsonify({"word": next_word.word})

    # reviewed_words = db.session.query(UserProgress.word_id).filter_by(user_id=user_id).subquery()
    # new_word = Dictionary.query.filter(~Dictionary.id.in_(reviewed_words)).order_by(Dictionary.frequency, db.func.random()).first()
    # if new_word:
    #     return jsonify({"word": new_word.word})
    # else:
    #     return jsonify({"message": "No new words to review"}), 404

# Get word definition
@app.route("/api/definition/<word>", methods=["GET"])
@jwt_required()
def get_definition(word):
    word_entry = Dictionary.query.filter_by(word=word).first()
    if word_entry:
        return jsonify({
            "definition": word_entry.definition,
            "synonym1" : word_entry.synonym1,
            "synonym2" : word_entry.synonym2,
            "sentence1" : word_entry.sentence1,
            "sentence2" : word_entry.sentence2,
        })
    return jsonify({"message": "Word not found"}), 404

# Submit recall rating (protected)
@app.route("/api/rate", methods=["POST"])
@jwt_required()
def submit_rating():
    data = request.json
    user_id = get_jwt_identity()
    word = data.get("word")
    q = data.get("rating")

    word_entry = Dictionary.query.filter_by(word=word).first()
    if not word_entry:
        return jsonify({"message": "Word not found"}), 404
    
    user_progress = UserProgress.query.filter_by(user_id=user_id, word_id=word_entry.id).first()

    if not user_progress:
        n = -1 # First time we're seeing the word
        interval = 0
        EF = 2.5 # Default value
    else:
        n = user_progress.n
        interval = user_progress.interval
        EF = user_progress.EF

    new_n, new_EF, new_interval = sm_2(q, n, EF, interval)
    # due_date = datetime.date.today() + datetime.timedelta(days=new_interval)
    due_date = (datetime.date.today() + datetime.timedelta(days=new_interval)).strftime("%Y-%m-%d")

    new_progress = UserProgress(
        user_id=user_id, word_id=word_entry.id, n=new_n, interval=new_interval, EF=new_EF, due_date=due_date
    )   

    if not user_progress:
        db.session.add(new_progress)
    else:
        UserProgress.query.filter_by(user_id=user_id, word_id=word_entry.id).update(
            {UserProgress.n: new_n, UserProgress.interval: new_interval, UserProgress.EF: new_EF, UserProgress.due_date: due_date}
        )

    db.session.commit()

    return jsonify({
        "message": "Rating submitted",
        "word" : word,
        "new_n" : new_n,
        "new_EF" : new_EF,
        "new_interval" : new_interval,
        "due_date" : due_date
    }), 200


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
