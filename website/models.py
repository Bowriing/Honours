#database models
from . import db #from website package
from flask_login import UserMixin
from sqlalchemy.sql import func

#class from tutorial can change to csv when needed
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000)) # set maxc len of string
    date = db.Column(db.DateTime(timezone=True), default=func.now()) #auto assign time/date to entry
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))#lowercasem user as sql doesnt ake capital into account
    
class CSVData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(300))
    file_path = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)#unique for userid as a user should only have 1 csv upload - a 1 to 1 relationship

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(500))
    firstName = db.Column(db.String(150))
    notes = db.relationship('Note')
    csv_data = db.relationship('CSVData', uselist=False, backref='user')
    
