from flask import render_template, redirect, request, url_for, session, flash, make_response, jsonify
from . import app, db
from .models import User, Balance, Transaction
import hashlib
from .crypto_client import get_crypto_curency_icon, get_top_cryptocurrencies, get_market_info, get_crypto_details
from sqlalchemy import extract, func
from datetime import datetime


def get_monthly_transaction_sum(user_id):
    current_year = datetime.now().year
    monthly_sums = db.session.query(
        extract('month', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        extract('year', Transaction.date) == current_year
    ).group_by('month').all()

    monthly_sums_dict = {month: 0 for month in range(1, 13)}
    for month, total in monthly_sums:
        monthly_sums_dict[month] = total

    return [monthly_sums_dict[month] for month in sorted(monthly_sums_dict)]


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
    current_balance = user.balance.current_balance if user.balance else 0

    month_transaction_sum = get_monthly_transaction_sum(user.id)

    return render_template("account.html", current_balance=current_balance, month_transaction_sum=month_transaction_sum)


@app.route("/payment", methods=['POST', 'GET'])
def payment():
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        return redirect(url_for("homepage", amount=amount, title=title))
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


@app.route("/currency_details/<string:currency_id>", methods=['GET'])
def current_details_view(currency_id):
    try:
        crypto_details = get_crypto_details(currency_id)
        if crypto_details:
            return render_template("currency_details.html", crypto_details=crypto_details)
        else:
            return make_response(jsonify({'error': 'Nie udało się pobrać danych szczegółowych o walucie.'}), 404)
    except Exception as e:
        print(e)
        return make_response(jsonify({'error': 'Wystąpił błąd podczas przetwarzania żądania.'}), 500)


@app.route("/")
def homepage():
    cryptocurrencies_data = get_top_cryptocurrencies()
    market_info = get_market_info()
    session_status = 'username' in session
    
    return render_template("index.html", session_status=session_status, cryptocurrencies_data=cryptocurrencies_data, market_info=market_info)


if __name__ == "__main__":
    app.run(debug=True)


@app.before_request 
def create_tables():
    db.create_all()

@app.context_processor
def inject_user_status():
    return dict(session_status='username' in session)
