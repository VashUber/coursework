from enum import unique
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(54), unique=True)
    password = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(54), nullable=True)
    old = db.Column(db.Integer)
    name = db.Column(db.String(90))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/registration', methods=("POST", "GET"))
def registration():
    return render_template('reg.html', title="Регистрация")

if __name__ == '__main__':
    app.run(debug=True)