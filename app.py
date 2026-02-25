
from flask import Flask, render_template, request, redirect, session
from database import get_db, init_db
from model import predict_email
from werkzeug.security import generate_password_hash, check_password_hash
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

import re
import random

app = Flask(__name__)
app.secret_key = "secret"

init_db()

# ---------------- PASSWORD & EMAIL VALIDATION ----------------
def is_valid_password(password):
    return password.strip() != ""


def is_valid_email(email):
    return re.fullmatch(r"[a-zA-Z0-9]+@myemail\.com", email)

#--------------admin----------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            message = "Invalid admin credentials"

    return render_template("admin_login.html", message=message)

#-----------------admin_dashboard-------

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = get_db()

    users = conn.execute(
        "SELECT id, name, email, phone FROM users"
    ).fetchall()

    reset_requests = conn.execute(
        """
        SELECT users.name, users.email, password_reset_requests.otp
        FROM password_reset_requests
        JOIN users ON users.email = password_reset_requests.email
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        reset_requests=reset_requests
    )


#-----------------admin_reset_password-----------

@app.route("/admin/reset/<int:user_id>", methods=["GET", "POST"])
def admin_reset_password(user_id):
    if not session.get("admin"):
        return redirect("/admin")

    message = ""

    if request.method == "POST":
        new_password = request.form["password"]

        if not is_strong_password(new_password):
            message = "Weak password"
        else:
            hashed = generate_password_hash(new_password)

            conn = get_db()
            conn.execute(
                "UPDATE users SET password=? WHERE id=?",
                (hashed, user_id)
            )
            conn.commit()
            conn.close()

            return redirect("/admin/dashboard")

    return render_template("admin_reset_password.html", message=message)

#----------------admin_logout-----------

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/login")   # ✅ redirect to user login page



# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect("/login")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    email_value = ""

    if request.method == "POST":
        email_value = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?", (email_value,)
        ).fetchone()
        conn.close()

        if not user:
            message = "Email not registered"
        elif not check_password_hash(user["password"], password):
            message = "Wrong password"
        else:
            session["user"] = email_value
            session["name"] = user["name"]
            return redirect("/inbox")

    return render_template(
        "login.html",
        message=message,
        email_value=email_value
    )


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    # store form values
    form_data = {
        "name": "",
        "surname": "",
        "email": "",
        "phone": ""
    }

    if request.method == "POST":
        form_data["name"] = request.form["name"]
        form_data["surname"] = request.form["surname"]
        form_data["email"] = request.form["email"]
        form_data["phone"] = request.form["phone"]
        password = request.form["password"]

        # Email format check
        if not is_valid_email(form_data["email"]):
            message = "Email must be like username@myemail.com"
            return render_template("register.html", message=message, form_data=form_data)

        # Password check (allow anything, not empty)
        if not is_valid_password(password):
            message = "Password cannot be empty"
            return render_template("register.html", message=message, form_data=form_data)

        conn = get_db()
        cur = conn.cursor()

        # Check if user already exists
        cur.execute("SELECT * FROM users WHERE email=?", (form_data["email"],))
        if cur.fetchone():
            conn.close()
            message = "User already registered"
            return render_template("register.html", message=message, form_data=form_data)

        hashed_password = generate_password_hash(password)

        # Insert user
        cur.execute("""
            INSERT INTO users (name, surname, email, password, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (
            form_data["name"],
            form_data["surname"],
            form_data["email"],
            hashed_password,
            form_data["phone"]
        ))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html", message=message, form_data=form_data)


# ---------------- INBOX ----------------

@app.route("/inbox")
def inbox():
    if "user" not in session:
        return redirect("/login")

    email = session["user"]
    conn = get_db()

    mails = conn.execute(
        "SELECT sender, subject, message FROM emails WHERE receiver=? AND is_spam=0",
        (email,)
    ).fetchall()

    # ✅ counts
    inbox_count = conn.execute(
        "SELECT COUNT(*) FROM emails WHERE receiver=? AND is_spam=0",
        (email,)
    ).fetchone()[0]

    spam_count = conn.execute(
        "SELECT COUNT(*) FROM emails WHERE receiver=? AND is_spam=1",
        (email,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "inbox.html",
        mails=mails,
        inbox_count=inbox_count,
        spam_count=spam_count
    )


# ---------------- SENT ----------------

@app.route("/sent")
def sent():
    if "user" not in session:
        return redirect("/login")

    email = session["user"]
    conn = get_db()
    mails = conn.execute(
        "SELECT receiver, subject, message FROM emails WHERE sender=?",
        (email,)
    ).fetchall()
    conn.close()

    return render_template("sent.html", mails=mails)

# ---------------- COMPOSE ----------------

# ---------------- COMPOSE ----------------

@app.route("/compose", methods=["GET", "POST"])
def compose():
    if "user" not in session:
        return redirect("/login")

    message_error = ""
    email = session["user"]

    conn = get_db()

    # ✅ COUNTS FOR SIDEBAR
    inbox_count = conn.execute(
        "SELECT COUNT(*) FROM emails WHERE receiver=? AND is_spam=0",
        (email,)
    ).fetchone()[0]

    spam_count = conn.execute(
        "SELECT COUNT(*) FROM emails WHERE receiver=? AND is_spam=1",
        (email,)
    ).fetchone()[0]

    if request.method == "POST":
        sender = email
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        message = request.form["message"]

        # ✅ CHECK IF RECEIVER EXISTS
        receiver_user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (receiver,)
        ).fetchone()

        if not receiver_user:
            conn.close()
            message_error = "This email is not registered"
            return render_template(
                "compose.html",
                error=message_error,
                inbox_count=inbox_count,
                spam_count=spam_count
            )

        # ✅ SPAM CHECK
        is_spam = predict_email(subject + " " + message)

        # ✅ INSERT EMAIL
        conn.execute(
            "INSERT INTO emails (sender, receiver, subject, message, is_spam) VALUES (?, ?, ?, ?, ?)",
            (sender, receiver, subject, message, is_spam)
        )

        conn.commit()
        conn.close()

        return redirect("/inbox")

    conn.close()

    return render_template(
        "compose.html",
        inbox_count=inbox_count,
        spam_count=spam_count
    )



# ---------------- SPAM ----------------

@app.route("/spam")
def spam():
    if "user" not in session:
        return redirect("/login")

    email = session["user"]
    conn = get_db()

    mails = conn.execute(
        "SELECT sender, subject, message FROM emails WHERE receiver=? AND is_spam=1",
        (email,)
    ).fetchall()

    inbox_count = conn.execute(
        "SELECT COUNT(*) FROM emails WHERE receiver=? AND is_spam=0",
        (email,)
    ).fetchone()[0]

    spam_count = conn.execute(
        "SELECT COUNT(*) FROM emails WHERE receiver=? AND is_spam=1",
        (email,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "spam.html",
        mails=mails,
        inbox_count=inbox_count,
        spam_count=spam_count
    )


# ---------------- FORGOT PASSWORD ----------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = ""

    if request.method == "POST":
        email = request.form["email"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?", (email,)
        ).fetchone()

        if not user:
            conn.close()
            message = "Email not registered"
            return render_template("forgot_password.html", message=message)

        otp = str(random.randint(100000, 999999))

        conn.execute(
            "INSERT INTO password_reset_requests (email, otp) VALUES (?, ?)",
            (email, otp)
        )
        conn.commit()
        conn.close()

        message = "OTP request sent to admin. Please contact admin."
        return render_template("forgot_password.html", message=message)

    return render_template("forgot_password.html", message=message)


# ---------------- VERIFY OTP ----------------

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    message = ""

    if request.method == "POST":
        entered_otp = request.form["otp"]

        conn = get_db()
        record = conn.execute(
            "SELECT * FROM password_reset_requests WHERE otp=?",
            (entered_otp,)
        ).fetchone()
        conn.close()

        if record:
            session["reset_email"] = record["email"]
            session["verified_otp"] = entered_otp
            return redirect("/reset-password")
        else:
            message = "Invalid OTP"

    return render_template("verify_otp.html", message=message)


# ---------------- RESET PASSWORD ----------------

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_email" not in session or "verified_otp" not in session:
        return redirect("/login")

    message = ""

    if request.method == "POST":
        password = request.form["password"]

        if not is_valid_password(password):
            message = "Password cannot be empty"
            return render_template("reset_password.html", message=message)

        hashed_password = generate_password_hash(password)

        conn = get_db()

        # ✅ update password
        conn.execute(
            "UPDATE users SET password=? WHERE email=?",
            (hashed_password, session["reset_email"])
        )

        # ✅ DELETE OTP AFTER USE
        conn.execute(
            "DELETE FROM password_reset_requests WHERE otp=?",
            (session["verified_otp"],)
        )

        conn.commit()
        conn.close()

        # ✅ clear sessions
        session.pop("reset_email", None)
        session.pop("verified_otp", None)

        return redirect("/login")

    return render_template("reset_password.html", message=message)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request
from spam_classifier import predict_email

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = ""
    if request.method == "POST":
        email_text = request.form["email"]
        prediction = predict_email(email_text)

    return render_template("index.html", prediction=prediction)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



