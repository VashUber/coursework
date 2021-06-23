from enum import unique
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.secret_key= '1482gfgfd121df fd;;;1221*32fdvd fuheioABOBA'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(54), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(54), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(90), nullable=False)
    ticket_id = db.Column(db.Integer, unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Ticket(db.Model):
    ticket_id = db.Column(db.Integer, db.ForeignKey("profiles.ticket_id"), primary_key=True)
    date_start = db.Column(db.DateTime, default=datetime.utcnow())
    date_end = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(days= 30))

class Clubs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(54), nullable=False)
    address = db.Column(db.Text, nullable=False)
    client_card = db.Column(db.Integer, db.ForeignKey("ticket.ticket_id"))

class Trainers(db.Model):
    id_trainer = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    schedule = db.Column(db.String(60), default = 'Пн - Сб')
    id_club = db.Column(db.Integer, db.ForeignKey("clubs.id"))




@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)   

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    base = create_engine('sqlite:///base.db').raw_connection()
    cursor = base.cursor()
    sql = "SELECT * FROM profiles WHERE id = " + str(current_user.id)
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template('profile.html', data = data)

@app.route('/login', methods=("POST", "GET"))
def loginPage():
    if request.method == "POST":
        login = request.form['email']
        password = request.form['password']

        if login and password:
            user = Users.query.filter_by(email = login).first()

            if user and check_password_hash(user.password, password):
                login_user(user)   

                return redirect(url_for('home'))
            else:
                flash('Ошибка входа')
                return redirect(url_for('loginPage'))

    else:
        return render_template('login.html')

@app.route('/logout', methods=("GET", "POST"))
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/registration', methods=("POST", "GET"))
def registration():
    if request.method == "POST":
        try:
            hash = generate_password_hash(request.form['password'])
            u = Users(email=request.form['email'], password=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=request.form['name'], age=request.form['age'], city=request.form['city'], user_id=u.id)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
    return render_template('reg.html', title="Регистрация")

if __name__ == '__main__':
    app.run(debug=True)