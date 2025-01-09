import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///expense.db")

# Define a list of categories
CATEGORIES = [
    "Shopping",
    "Entertainments",
    "Bills & Utilities",
    "Education",
    "Transport",
    "Food",
    "Health & Wellness"
]

# Define a list of stars
STARS = [
    "*****",
    "****",
    "***",
    "**",
    "*"
]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show transactions filtered by time"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user_id = session["user_id"]

        # Ensure time was submitted
        time = request.form.get("filter")
        if not time:
            return apology("must provide time")

        # Query necessary details in transactions table
        transactions_db = db.execute(
            "SELECT description, category, price, date FROM transactions WHERE user_id = ? AND date LIKE ?", user_id, f"{time}%"
        )

        # Get the available cash of user
        cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = cash_db[0]["cash"]

        # Get the total value of selected items
        total_value = 0
        for row in transactions_db:
            total_value += row["price"]

        # Show expected result
        return render_template("filter.html", transactions=transactions_db, cash=cash, total_value=total_value)
    
    # # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username is exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to homepage
        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username")
        
        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password")
        
        # Ensure password confirmation was submitted
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide confirmation")
        
        # Ensure confirmation
        if password != confirmation:
            return apology("password do not match")
        
        # Hash password
        hash = generate_password_hash(password)

        # Checking if username already exists
        try:
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except ValueError:
            return apology("username already exists")
        
        # Set new user session
        session["user_id"] = new_user

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
    # Redirect to homepage
    return redirect("/")


@app.route("/insert", methods=["GET", "POST"])
@login_required
def insert():
    """Insert a new item user have purchased"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure description was submitted correctly
        description = request.form.get("description")
        if not description:
            return apology("must provide description")
        
        # Ensure category was submitted correctly
        category = request.form.get("category")
        if not category:
            return apology("must provide category")
        
        # Ensure price was submitted correctly
        price = int(request.form.get("price")) # Convert price to integer
        if not price:
            return apology("must provide cash")
        elif price <= 0:
            return apology("price must be greater than 0")

        # Get user's cash        
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        # Ensure user have enough money
        if user_cash < price:
            return apology("do not have enough money")
        
        # Update available cash
        update_cash = user_cash - price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)
        
        # Get date and time now
        date = datetime.datetime.now()

        # Insert informations into transactions table
        db.execute(
            "INSERT INTO transactions (user_id, description, category, price, date) VALUES (?, ?, ?, ?, ?)",
            user_id, description, category, price, date)
        
        # Flash notification
        flash("Insert Successfully!")
        
        # Return
        return render_template("insert.html", categories=CATEGORIES)
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("insert.html", categories=CATEGORIES)
    

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete an item user have bought"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure date was submitted correctly
        date = request.form.get("date")
        if not date:
            return apology("must provide date")
        
        # Get user cash
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        # Update user cash after deleting item
        price_db = db.execute(
            "SELECT price FROM transactions WHERE user_id = ? AND date = ?", user_id, date
        )
        price = price_db[0]["price"]
        update_cash = user_cash + price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)
        
        # Delete item
        db.execute("DELETE FROM transactions WHERE user_id = ? AND date = ?", user_id, date)

        # Flash notification
        flash("Delete successfully!")

        # Return
        return render_template("delete.html")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("delete.html")
    

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Get all the history of purchasing"""

    # Get data
    user_id = session["user_id"]
    rows = db.execute(
        "SELECT description, category, price, date FROM transactions WHERE user_id = ?", user_id
    )

    # Show data
    return render_template("history.html", rows=rows)


@app.route("/top_up", methods=["GET", "POST"])
@login_required
def top_up():
    """Top up money"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure money is submitted correctly
        money = int(request.form.get("top_up"))
        if not money:
            return apology("must provide money")
        elif money <= 0:
            return apology("money must be greater than 0")
        
        # Get user cash
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        # Update user cash
        update_cash = user_cash + money
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        # Flash notification
        flash(f"Top up successfully! Available cash: ${update_cash:,.2f}")

        # Return
        return render_template("top_up.html", user_cash=update_cash)
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get user cash
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        return render_template("top_up.html", user_cash=user_cash)
    

@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    """Withdraw money"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure money is submitted correctly
        money = int(request.form.get("withdraw"))
        if not money:
            return apology("must provide money")
        elif money <= 0:
            return apology("money must be greater than 0")
        
        # Get user cash
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        # Ensure money withdrawed is not greater than current user cash
        if money > user_cash:
            return apology("not have enough amount of money to withdraw")

        # Update user cash
        update_cash = user_cash - money
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        # Flash notification
        flash(f"Withdraw successfully! Available cash: ${update_cash:,.2f}")

        # Return
        return render_template("withdraw.html", user_cash=update_cash)
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get user cash
        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        return render_template("withdraw.html", user_cash=user_cash)
    

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    """Get feedback"""
    if request.method == "POST":
        star = request.form.get("star")
        if not star:
            return apology("must provide stars")
        
        comment = request.form.get("comment")
        if not comment:
            return apology("must provide comment")
        
        user_id = session["user_id"]
        db.execute(
            "INSERT INTO feedbacks (user_id, star, comment) VALUES (?, ?, ?)",
            user_id, star, comment
        )

        feedbacks = db.execute("SELECT * FROM feedbacks ORDER BY id DESC")

        flash("Feedback Submitted Successfully!")

        return render_template("feedbacked.html", feedbacks=feedbacks)
        
    else:
        return render_template("feedback.html", stars=STARS)