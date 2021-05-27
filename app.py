from enum import unique
from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    city= db.Column(db.String(90))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/registration', methods=("POST", "GET"))
def registration():
    if request.method == "POST":
        try:
            hash = generate_password_hash(request.form['password'])
            u = Users(email=request.form['email'], password=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=request.form['name'], old=request.form['old'], city=request.form['city'], user_id=u.id)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
    return render_template('reg.html', title="Регистрация")

if __name__ == '__main__':
    app.run(debug=True)