from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import crypto_client
from sqlalchemy import extract, func
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "ninininin"

db = SQLAlchemy(app)

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
    amount = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_request 
def create_tables():
    db.create_all()

@app.context_processor
def inject_user_status():
    return dict(session_status='username' in session)

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

@app.route("/currency/<int:currency_id>/purchase", methods=['POST', 'GET'])
def purchase_currency(currency_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash("Błąd: użytkownik niezalogowany.", 'error')
        return redirect(url_for('login'))
    
    cryptocurrencies = crypto_client.get_top_cryptocurrencies()
    if currency_id < len(cryptocurrencies):
        currency = cryptocurrencies[currency_id]
        currency_name = currency['name']
        currency_price = currency['current_price']
    else:
        flash('Nie znaleziono waluty.', 'error')
        return redirect(url_for('homepage'))
    
    if request.method == 'POST':
        amount = float(request.form['amount'])
        purchase_price = currency_price * amount
        new_transaction = Transaction(user_id=user.id, currency_id=currency_id, amount=amount, purchase_price=purchase_price)

        db.session.add(new_transaction)
        db.session.commit()
        
        flash(f'Zakupiono {amount} {currency_name} za {purchase_price} USD.', 'success')
        return redirect(url_for('account'))
    
    return render_template('purchase_currency.html', currency=currency, currency_id=currency_id)

@app.route("/")
def homepage():
    crypto_icon = crypto_client.get_crypto_curency_icon(coin_id='bitcoin')
    cryptocurrencies_data = crypto_client.get_top_cryptocurrencies()
    market_info = crypto_client.get_market_info()
    session_status = 'username' in session
    
    return render_template("index.html", session_status=session_status, cryptocurrencies_data=cryptocurrencies_data, market_info=market_info, crypto_icon=crypto_icon)

if __name__ == "__main__":
    app.run(debug=True)
