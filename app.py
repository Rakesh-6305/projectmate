from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(name)
app.secret_key = "projectmate"

---------------- DATABASE ----------------

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)

---------------- FOLDERS ----------------

BASE_DIR = os.path.abspath(os.path.dirname(file))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "static")
app.config['DELIVERIES_FOLDER'] = os.path.join(BASE_DIR, "deliveries")
os.makedirs(app.config['DELIVERIES_FOLDER'], exist_ok=True)

---------------- EMAIL SAFE CONFIG ----------------

Render free hosting lo SMTP crash avoid cheyyadaniki

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

KEEP EMPTY → EMAIL DISABLED MODE

app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''

mail = Mail(app)

---------------- ADMIN ----------------

ADMIN_USERNAME = "Rakesh6305"
ADMIN_PASSWORD = "Rakesh630@"

---------------- MODELS ----------------

class User(db.Model):
id = db.Column(db.Integer, primary_key=True)
username = db.Column(db.String(100), unique=True)
email = db.Column(db.String(150))
password = db.Column(db.String(100))

class Project(db.Model):
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(200))
price = db.Column(db.Integer)

class Order(db.Model):
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(db.Integer)
project_id = db.Column(db.Integer)
status = db.Column(db.String(50), default="Pending Approval")
payment_status = db.Column(db.String(50), default="Not Paid")
project_file = db.Column(db.String(300), default="")

---------------- SAFE EMAIL FUNCTION ----------------

def send_update_email(target_email, subject, body):
try:
# EMAIL DISABLED → SKIP
if not app.config.get("MAIL_USERNAME"):
print("Email disabled. Skipping email.")
return

    msg = Message(subject, recipients=[target_email])
    msg.body = body
    mail.send(msg)
    print("Email sent successfully")

except Exception as e:
    print("Email error ignored:", e)

---------------- ROUTES ----------------

@app.route("/")
def home():
return render_template("index.html")

@app.route("/register", methods=["POST","GET"])
def register():
if request.method == "POST":
user = User(
username=request.form["username"],
email=request.form["email"],
password=request.form["password"]
)
db.session.add(user)
db.session.commit()
flash("Registered successfully")
return redirect("/login")
return render_template("register.html")

@app.route("/login", methods=["POST","GET"])
def login():
if request.method == "POST":
user = User.query.filter_by(
username=request.form["username"],
password=request.form["password"]
).first()

    if user:
        session["user"] = user.id
        session["username"] = user.username
        return redirect("/dashboard")

    flash("Invalid login")

return render_template("login.html")

@app.route("/logout")
def logout():
session.clear()
return redirect("/login")

@app.route("/dashboard")
def dashboard():
if "user" not in session:
return redirect("/login")

orders = Order.query.filter_by(user_id=session["user"]).all()
return render_template("dashboard.html", orders=orders)

@app.route("/projects")
def projects():
projects = Project.query.all()
return render_template("projects.html", projects=projects)

@app.route("/place_order/"int:id" (int:id)")
def place_order(id):
if "user" not in session:
return redirect("/login")

order = Order(user_id=session["user"], project_id=id)
db.session.add(order)
db.session.commit()

flash("Order placed!")
return redirect("/dashboard")

---------------- ADMIN ----------------

@app.route("/admin_login", methods=["POST","GET"])
def admin_login():
if request.method == "POST":
if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
session["admin"] = True
return redirect("/admin")

return render_template("admin_login.html")

@app.route("/admin")
def admin():
if "admin" not in session:
return redirect("/admin_login")

orders = Order.query.all()
return render_template("admin.html", orders=orders)

@app.route("/approve/"int:id" (int:id)")
def approve_order(id):
order = Order.query.get(id)
order.status = "Approved"
db.session.commit()

user = User.query.get(order.user_id)
send_update_email(user.email,
    "Project Approved",
    "Your project approved. Please proceed payment."
)

return redirect("/admin")

@app.route("/confirm_payment/"int:id" (int:id)")
def confirm_payment(id):
order = Order.query.get(id)
order.payment_status = "Confirmed"
db.session.commit()

user = User.query.get(order.user_id)
send_update_email(user.email,
    "Payment Confirmed",
    "Payment confirmed successfully."
)

flash("Payment confirmed")
return redirect("/admin")

---------------- DOWNLOAD ----------------

@app.route("/download/"int:id" (int:id)")
def download(id):
order = Order.query.get(id)

if order.payment_status != "Confirmed":
    flash("Payment not confirmed")
    return redirect("/dashboard")

return send_from_directory(
    app.config['DELIVERIES_FOLDER'],
    order.project_file,
    as_attachment=True
)

---------------- INIT DATABASE ----------------

with app.app_context():
db.create_all()

if Project.query.count() == 0:
    db.session.add(Project(name="Frontend Portfolio Website", price=999))
    db.session.add(Project(name="React Admin Dashboard", price=1999))
    db.session.commit()

---------------- RUN ----------------

if name == "main":
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
