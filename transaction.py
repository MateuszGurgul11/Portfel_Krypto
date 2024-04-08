from sqlalchemy import extract, func
from datetime import datetime
from app import db, Transaction

def get_monthly_transaction_sum(user_id):
    current_year = datetime.now().year
    monthly_sums = db.session.query(
        extract('month', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        extract('year', Transaction.date) == current_year
    ).group_by(
        extract('month', Transaction.date)
    ).all()

    monthly_sums_dict = {month: 0 for month in range(1, 13)}
    for month, total in monthly_sums:
        monthly_sums_dict[month] = total

    monthly_sums_list = [monthly_sums_dict[month] for month in sorted(monthly_sums_dict)]
    return monthly_sums_list
 