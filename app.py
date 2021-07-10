from enum import unique
from operator import eq
import os
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, event
from sqlalchemy.engine import  Engine
from sqlite3 import Connection as SQLite3Connection
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)

app.secret_key= '1482gfgfd121df fd;;;1221*32fdvd fuheioABOBA'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:aq1sw2de3@localhost/IG'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["IMAGE_UPLOADS"] = './static/img/upload_profile/'
app.config["IMAGE_CLUBS"] = './static/img/clubs/'
app.config["IMAGE_TRAINERS"] = './static/img/trainers'
app.config["IMAGE_EQUIPMENT"] = './static/img/equipment'
db = SQLAlchemy(app)

login_manager = LoginManager(app)




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
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    price = db.Column(db.Integer, nullable=False, default = 1200)

class Clubs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(54), nullable=False)
    address = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)

class Trainers(db.Model):
    id_trainer = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    schedule = db.Column(db.String(60), default = 'Пн - Сб')
    id_club = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    image = db.Column(db.Text, nullable = True)
    work_experience = db.Column(db.Integer, nullable = False)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    image = db.Column(db.Text, nullable = False)
    name  = db.Column(db.String(90), nullable = False)

admin = Admin(app)
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Profiles, db.session))
admin.add_view(ModelView(Ticket, db.session))
admin.add_view(ModelView(Clubs, db.session))
admin.add_view(ModelView(Trainers, db.session))
admin.add_view(ModelView(Equipment, db.session))

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)   

@app.route('/')
@app.route('/home')
def home():
    clubs = Clubs.query.limit(4).all()
    clubs_count = Clubs.query.count()
    return render_template('home.html', clubs = clubs, count = clubs_count)


@app.route('/profile', methods=["POST", "GET"])
def profile():
    data = db.session.query(Profiles, Users
    ).filter(Profiles.id == current_user.id
    ).filter(Profiles.user_id == Users.id).all()
    ticket = db.session.query(Profiles, Ticket
    ).filter(Ticket.ticket_id == current_user.id
    ).filter(Profiles.user_id == current_user.id
    ).all()
    clubs = Clubs.query.all()
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
            col = Profiles.query.filter_by(id = current_user.id).update({Profiles.image: path})
            db.session.commit()

            return redirect(request.url) 
        
        if request.form and form_id == 1:
            name = request.form['fullname']
            city = request.form['city']
            email = request.form['email']
            profile = Profiles.query.filter_by(id = current_user.id).update({Profiles.name: name, Profiles.city: city})
            user = Users.query.filter_by(id = current_user.id).update({Users.email: email})
            
            db.session.commit()

            return redirect(request.url)

        if request.form and form_id == 2:
            club = request.form['club-name']
            profile = Profiles.query.filter_by(id = current_user.id).update({Profiles.ticket_id: current_user.id})
            ticket = Ticket(ticket_id = current_user.id, club_id = club)
            db.session.add(ticket)
            db.session.commit()
            return redirect(request.url)
    return render_template('profile.html', data = data, clubs=clubs, ticket=ticket)

@app.route('/ticket')
def ticket():
    ticket = db.session.query(Profiles, Ticket, Clubs
    ).filter(Profiles.id == current_user.id
    ).filter(Profiles.ticket_id == Ticket.ticket_id
    ).filter(Ticket.club_id == Clubs.id).all()
    return render_template('ticket.html', ticket=ticket)

@app.route('/trainers', methods=["POST", "GET"])
def trainers():
    trainers = db.session.query(Clubs, Trainers
    ).filter(Trainers.id_club == Clubs.id).all()
    count = Trainers.query.count()
    sumExp = db.session.query(func.sum(Trainers.work_experience)).all()
    if request.method == 'POST':
        name = request.form['name']
        schedule = request.form['schedule']
        id_club = request.form['id_club']
        work_experience = request.form['work_experience']
        image = request.files['image']
        image.save(os.path.join(app.config["IMAGE_TRAINERS"], image.filename))
        trainer = Trainers(name=name, schedule=schedule, 
        id_club=id_club, image=image.filename, work_experience=work_experience)
        db.session.add(trainer)
        db.session.commit()
        return redirect(request.url)

    return render_template('trainers.html', trainers=trainers, count=count, sumExp=sumExp)

@app.route('/equipment', methods=["POST", "GET"])
def equipment():
    equipment = Equipment.query.all()
    count = Equipment.query.count()
    if request.method == "POST":
        name = request.form["name"]
        club_id = request.form["club_id"]
        image = request.files["image"]
        image.save(os.path.join(app.config["IMAGE_EQUIPMENT"], image.filename))
        equipment = Equipment(name=name, club_id=club_id, image=image.filename)

        db.session.add(equipment)
        db.session.commit()
        return redirect(request.url)

    return render_template('equipment.html', equipment=equipment, count=count)

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

@app.route('/clubs', methods=("POST", "GET"))
def clubs():
    if request.method == "POST":
        name = request.form['name']
        address = request.form['address']
        image = request.files['image']
        image.save(os.path.join(app.config["IMAGE_CLUBS"], image.filename))
        club = Clubs(name = name, address=address, image=image.filename)
        db.session.add(club)
        db.session.commit()
        return redirect(request.url)

    clubs = Clubs.query.all()
    clubs_count = Clubs.query.count()
    return render_template('clubs.html', clubs = clubs, count = clubs_count)

if __name__ == '__main__':
    app.run(debug=True)