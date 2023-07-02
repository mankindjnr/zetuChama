from flask_login import UserMixin
from . import db
import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    name = db.Column(db.String(1000))

class Manager(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    name = db.Column(db.String(1000))

class Chamas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chama_name = db.Column(db.String(100), unique=True)
    requirements = db.Column(db.String(1350))
    description = db.Column(db.String(1350))
    summary = db.Column(db.String(800))
    manager = db.Column(db.String(100))
    date_created = db.Column(db.Date, default=datetime.date.today)
    time_created = db.Column(db.Time, default=datetime.datetime.now().time())

    def __init__(self, chama_name, requirements, description, summary, manager):
        self.chama_name = chama_name
        self.requirements = requirements
        self.description = description
        self.summary = summary
        self.manager = manager
