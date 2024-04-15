from flask import render_template, redirect, request, url_for, session, flash, make_response, jsonify
from . import app, db
from .models import User, Balance, Transaction
import hashlib
from sqlalchemy import extract, func
from datetime import datetime


@app.route("/register", methods=['POST', 'GET'])
def register():
    session_status = False
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        user_exist = User.query.filter_by(username = username).first()
        if not user_exist:
            new_user = User(username = username, email = email, password = password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('homepage'))
    return render_template("register.html", session_status=session_status)


@app.route("/login", methods=['POST', 'GET'])
def login():
    session_status = False
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session_status = True
            session['username'] = username
            return redirect(url_for("homepage"))
        else:
            return "Dane są niepoprawne!"
    return render_template("login.html", session_status=session_status)


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("homepage"))

@app.route("/account")
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    transactions = Transaction.query.filter_by(user_id=user.id).all()
    current_balance = user.balance.current_balance if user.balance else 0

    return render_template("account.html", current_balance=current_balance, transactions=transactions)


@app.route("/payment", methods=['POST', 'GET'])
def payment():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        destination = request.form['destination']
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        user = User.query.filter_by(username=session['username']).first()

        new_transaction = Transaction(user_id=user.id, destination=destination, date=datetime.utcnow(), amount=amount)
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for("account", amount=amount, destination=destination, account_number=account_number))
    return render_template("payment.html")


@app.route("/add_funds", methods=['POST', 'GET'])
def add_funds():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        user = User.query.filter_by(username=session['username']).first()

        if user and user.balance:
            user.balance.current_balance += amount
        else:
            new_balance = Balance(user_id=user.id, current_balance=amount)
            db.session.add(new_balance)

        db.session.commit()
        return redirect(url_for('account'))
    return render_template('account.html')


@app.route("/")
def homepage():
    session_status = 'username' in session
    
    return render_template("index.html", session_status=session_status)

@app.before_request 
def create_tables():
    db.create_all()

@app.context_processor
def inject_user_status():
    return dict(session_status='username' in session)
