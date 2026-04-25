from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
db = SQLAlchemy(app)

app.config["SECRET_KEY"] = "your-secret-key"
app.config["SECRET_KEY"] = "mysecretkey123"
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    password = db.Column(db.String(128))
    @property
    def id(self):
        return self.user_id
class Transaction(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    amount = db.Column(db.Float)
    type = db.Column(db.String(10))
    category = db.Column(db.String(20))
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        if User.query.filter_by(username=username).first():
            flash("Username already taken, please choose another.")
            return redirect(url_for("register"))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user == None or bcrypt.check_password_hash(user.password, password) == False:
            flash("Invalid username or password.")
            return redirect(url_for("login"))
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    transactions = Transaction.query.filter_by(user_id=current_user.user_id).all()
    total_income = 0
    total_expense = 0
    category_totals = {}


    for transaction in transactions:
        if transaction.type == "income":
            total_income += transaction.amount
        elif transaction.type == "expense":
            total_expense += transaction.amount

        if transaction.category not in category_totals:
            category_totals[transaction.category] = 0
        category_totals[transaction.category] += transaction.amount

    total = total_income-total_expense

    return render_template("index.html", transactions=transactions, total=total, total_income = total_income, total_expense = total_expense, category_totals=category_totals)

@app.route("/add", methods =["POST"])
@login_required
def add_transaction():
    description = request.form["description"]
    amount = request.form["amount"]
    type = request.form["type"]
    category = request.form["category"]
    today = date.today()
    transaction = Transaction(description=description, amount=amount, type=type, category=category, date=today, user_id=current_user.user_id)
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get(id)
    if request.method == "POST":
        description = request.form["description"]
        amount = request.form["amount"]
        type = request.form["type"]
        category = request.form["category"]
        transaction.description = description
        transaction.amount = amount
        transaction.type = type
        transaction.category = category
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", transaction=transaction)

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for("home"))
if __name__ == "__main__":
    app.run(debug=False)