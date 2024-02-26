#database models
from . import db #from website package
from flask_login import UserMixin
from sqlalchemy.sql import func

class CSVData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    csv_content = db.Column(db.Text, nullable=True)#db.text for long lengths of text which the csv files will be 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)#unique for userid as a user should only have 1 csv upload - a 1 to 1 relationship

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(500))
    firstName = db.Column(db.String(150))
    csv_data = db.relationship('CSVData', uselist=False, backref='user')
    devices = db.relationship('Device', backref='user')
    custom_color = db.Column(db.String(7), nullable=True) #HEX Color Code

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceName = db.Column(db.String(150))
    deviceType = db.Column(db.String(50))
    powerRating = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    