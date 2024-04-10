from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), unique = True, nullable = False)
    email = db.Column(db.String(200))
    password = db.Column(db.String(100), nullable = False)
    balance = db.relationship('Balance', backref='user', uselist = False)

class Balance(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    current_balance = db.Column(db.Float, nullable = False, default = 0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) 
    amount = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)