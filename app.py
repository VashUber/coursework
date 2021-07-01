from enum import unique
import os
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, event
from sqlalchemy.engine import  Engine
from sqlite3 import Connection as SQLite3Connection
from datetime import datetime, timedelta
from sqlalchemy.sql.elements import Null
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import backref
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.secret_key= '1482gfgfd121df fd;;;1221*32fdvd fuheioABOBA'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(54), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    child = db.relationship('Profiles', backref="parent", passive_deletes=True)

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(54), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(90), nullable=False)
    ticket_id = db.Column(db.Integer, nullable=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), nullable=False, unique=True)
    image = db.Column(db.Text, nullable = True, default='./static/img/upload_profile/default.jpg')
    child = db.relationship('Ticket', backref="parent", passive_deletes=True)

class Ticket(db.Model):
    ticket_id = db.Column(db.Integer, db.ForeignKey("profiles.ticket_id", ondelete='CASCADE'), primary_key=True)
    date_start = db.Column(db.DateTime, default=datetime.now())
    date_end = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(days= 30))
    #club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)

class Clubs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(54), nullable=False)
    address = db.Column(db.Text, nullable=False)

class Trainers(db.Model):
    id_trainer = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    schedule = db.Column(db.String(60), default = 'Пн - Сб')
    id_club = db.Column(db.Integer, db.ForeignKey("clubs.id"))

#class Equipment(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
#   image = db.Column(db.Text, nullable = True)
#   name  = db.Column(db.String(90), nullable = True)



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)   

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

app.config["IMAGE_UPLOADS"] = './static/img/upload_profile/'

@app.route('/profile', methods=["POST", "GET"])
def profile():
    base = create_engine('sqlite:///base.db').raw_connection()
    cursor = base.cursor()
    sql = "SELECT * FROM profiles LEFT JOIN ticket on profiles.ticket_id = ticket.ticket_id WHERE id = " + str(current_user.id)
    cursor.execute(sql)
    data = cursor.fetchall()
    end = Ticket.query.filter_by(ticket_id = current_user.id).first()
    if (end):
        end = end.date_end
        if (end.strftime("%Y%m%d") <= datetime.utcnow().strftime("%Y%m%d")):
            Ticket.query.filter_by(ticket_id = current_user.id).delete()
            Profiles.query.filter_by(id = current_user.id).update({Profiles.ticket_id: None})
            db.session.commit()
            return redirect(request.url)

    if request.method == "POST":
        form_id = request.args.get('form_id', 1, type=int) 

        if request.files:
            image = request.files['image']
            if (not image):
                flash('Изображение не было прикреплено!')
                return redirect(request.url)

            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))

            path = './static/img/upload_profile/' + str(image.filename)
            sql = "UPDATE profiles SET image = ('" + path + "') WHERE id = " + str(current_user.id)
            cursor.execute(sql)
            base.commit()

            return redirect(request.url) 
        
        if request.form and form_id == 1:
            name = request.form['fullname']
            city = request.form['city']
            sql = "UPDATE profiles SET name = '" + name + "', city = '" + city + "' WHERE id = " + str(current_user.id) + ";"
            cursor.execute(sql)
            base.commit()

            return redirect(request.url)

        if request.form and form_id == 2:
            profile = Profiles.query.filter_by(id = current_user.id).update({Profiles.ticket_id: current_user.id})
            
            ticket = Ticket(ticket_id = current_user.id)
            db.session.add(ticket)
            db.session.commit()
            return redirect(request.url)

   
        
    return render_template('profile.html', data = data)

@app.route('/delete', methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        Users.query.filter_by(id = current_user.id).delete()
        logout_user()
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('delete.html')

@app.route('/login', methods=["POST", "GET"])
def loginPage():
    if request.method == "POST":
        login = request.form['email']
        password = request.form['password']

        if login and password:
            user = Users.query.filter_by(email = login).first()

            if user and check_password_hash(user.password, password):
                login_user(user)   

                return redirect(url_for('profile'))
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