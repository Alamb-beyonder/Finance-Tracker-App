from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    amount = db.Column(db.Float)
    type = db.Column(db.String(10))
    
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    total_income = 0
    total_expense = 0
    transactions = Transaction.query.all()

    for transaction in transactions:
        if transaction.type == "income":
            total_income += transaction.amount
        elif transaction.type == "expense":
            total_expense += transaction.amount

    total = total_income-total_expense
    return render_template("index.html", transactions=transactions, total=total, total_income = total_income, total_expense = total_expense)

@app.route("/about")
def about():
    return "This is a finance tracker app!"

@app.route("/add", methods =["POST"])
def add_transaction():
    description = request.form["description"]
    amount = request.form["amount"]
    type = request.form["type"]
    transaction = Transaction(description=description, amount=amount, type=type)
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>", methods=["POST"])
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for("home"))
if __name__ == "__main__":
    app.run(debug=True)