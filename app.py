from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "projectmate"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
app.config['DELIVERIES_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'deliveries')
os.makedirs(app.config['DELIVERIES_FOLDER'], exist_ok=True)

# ---------- EMAIL CONFIGURATION ----------
# [IMPORTANT] Update these with your real SMTP details to send actual emails.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
mail = Mail(app)

db = SQLAlchemy(app)

# ---------- ADMIN CREDENTIALS ----------
ADMIN_USERNAME = "Rakesh6305"
ADMIN_PASSWORD = "Rakesh630@"

# ---------- MODELS ----------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="Pending Approval")
    admin_remark = db.Column(db.Text, default="")
    # Payment details (filled after admin approval)
    transaction_id = db.Column(db.String(200), default="")
    mobile_number = db.Column(db.String(20), default="")
    email = db.Column(db.String(200), default="")
    payment_status = db.Column(db.String(50), default="Not Paid")
    project_file = db.Column(db.String(300), default="")

class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    sender = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CustomProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    problem = db.Column(db.Text)
    objective = db.Column(db.Text)
    outcome = db.Column(db.Text)
    status = db.Column(db.String(50), default="Requested")
    price = db.Column(db.Integer, default=0)
    transaction_id = db.Column(db.String(200), default="")
    mobile_number = db.Column(db.String(20), default="")
    email = db.Column(db.String(200), default="")
    payment_status = db.Column(db.String(50), default="Not Paid")
    balance_payment_status = db.Column(db.String(50), default="Not Paid")
    balance_transaction_id = db.Column(db.String(200), default="")
    output_file = db.Column(db.String(300), default="")
    project_file = db.Column(db.String(300), default="")

class CustomMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custom_project_id = db.Column(db.Integer, nullable=False)
    sender = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------- HELPER FUNCTIONS ----------

def send_update_email(target_email, subject, body):
    """Sends an email update to the student."""
    try:
        msg = Message(subject, recipients=[target_email])
        msg.body = body
        mail.send(msg)
        print(f"Email sent to {target_email}")
    except Exception as e:
        # We print the error but don't crash the app if email fails
        print(f"Failed to send email to {target_email}: {e}")

# ---------- CHATBOT AI ----------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    user_msg = data.get("message", "").lower().strip()
    
    import random
    greetings = ["Hi there! I'm the ProjectMate Assistant.", "Hello! How can I help you today?", "Hey! Ready to find or build your next project?"]
    personalities = ["I'm here to guide you through our process.", "I can help with pricing, payments, or delivery questions.", "Ask me anything about how ProjectMate works!"]

    # Advanced Local AI Logic
    # Pricing & Services
    if any(k in user_msg for k in ["price", "cost", "fee", "how much"]):
        responses = [
            "Our standard projects start at just ₹999. Custom projects are quoted individually based on your specific requirements.",
            "Standard UI/UX projects are usually ₹999-₹1999. For custom dev, just submit an idea and Rakesh will set a price for you!",
            "Standard projects have fixed prices listed on the 'Projects' page. Custom projects use a 50/50 payment model."
        ]
        response = random.choice(responses)
    
    # Payments
    elif any(k in user_msg for k in ["pay", "payment", "upi", "card", "transaction", "google pay", "phonepe"]):
        response = "We support all major UPI apps (Google Pay, PhonePe, Paytm). For standard projects, it's 100% upfront. For custom projects, you pay 50% to start and the remaining 50% once it's delivered but before the final source code download."
    
    # Delivery & Downloads
    elif any(k in user_msg for k in ["download", "get file", "delivery", "where is my project", "zip"]):
        response = "All your files live in your 'Dashboard'. Standard projects are ready instantly after payment confirmation. Custom projects unlock for download once the final 50% balance payment is confirmed by our team."
    
    # Refund & Policy
    elif any(k in user_msg for k in ["refund", "cancel", "return", "guarantee"]):
        response = "Because we deliver digital assets (source code), we typically don't offer refunds. However, we're committed to quality! For custom projects, we include 2 rounds of free revisions to make sure it's exactly what you need."
    
    # Technical / Support
    elif any(k in user_msg for k in ["help", "support", "rakesh", "contact", "issue", "error", "bug"]):
        response = "If you're facing a technical issue, please use the 'Chat with Admin' button on your dashboard. Our lead developer, Rakesh, usually checks messages every few hours. You can also reach him at +91 9491031780."
    
    # Project Types / Tech Stack
    elif any(k in user_msg for k in ["tech", "stack", "language", "python", "flask", "react", "html", "css"]):
        response = "We specialize in Python (Flask/Django), React, and Data Analytics projects. Most of our standard projects use clean HTML/CSS/JS for the frontend to ensure they're easy for you to customize!"

    # Greetings
    elif any(k in user_msg for k in ["hello", "hi", "hey", "who are you", "chatbot"]):
        response = f"{random.choice(greetings)} {random.choice(personalities)}"
        
    else:
        response = "That sounds interesting! While I'm still learning, I can give you details on pricing, payment methods, delivery times, or how to contact our support team. What would you like to know more about?"
        
    return {"response": response}

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        sting = User.query.filter_by(username=username).first()
        if existing:
            flash("Username already exists!", "error")
            return redirect("/register")

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect("/login")
    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            session["user"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid username or password!", "error")

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("username", None)
    flash("Logged out successfully!", "success")
    return redirect("/login")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    orders = db.session.query(Order, Project).join(
        Project, Order.project_id == Project.id
    ).filter(Order.user_id == session["user"]).all()

    custom_projects = CustomProject.query.filter_by(user_id=session["user"]).all()

    return render_template("dashboard.html", orders=orders, username=session.get("username"), custom_projects=custom_projects)

# ---------- PROJECTS ----------
@app.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

# ---------- PLACE ORDER (No payment at this stage) ----------
@app.route("/place_order/<int:id>")
def place_order(id):
    if "user" not in session:
        flash("Please login first!", "error")
        return redirect("/login")

    project = Project.query.get_or_404(id)

    order = Order(
        user_id=session["user"],
        project_id=id
    )
    db.session.add(order)
    db.session.commit()

    flash(f"Order placed for '{project.name}'! Wait for admin approval.", "success")
    return redirect("/dashboard")

# ---------- PAYMENT PAGE (After approval, pay half amount) ----------
@app.route("/payment/<int:order_id>", methods=["GET", "POST"])
def payment(order_id):
    if "user" not in session:
        return redirect("/login")

    order = Order.query.get_or_404(order_id)
    if order.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    if order.status != "Approved":
        flash("This order is not approved yet!", "error")
        return redirect("/dashboard")

    if order.payment_status == "Paid":
        flash("Payment already submitted!", "error")
        return redirect("/dashboard")

    project = Project.query.get(order.project_id)
    total_price = project.price

    if request.method == "POST":
        order.transaction_id = request.form["transaction_id"]
        order.mobile_number = request.form["mobile_number"]
        order.email = request.form["email"]
        order.payment_status = "Paid"
        db.session.commit()
        flash("Payment details submitted successfully!", "success")
        return redirect("/dashboard")

    return render_template("payment.html", order=order, project=project, total_price=total_price)

# ---------- ORDER CHAT (Student View) ----------
@app.route("/order_chat/<int:order_id>")
def order_chat(order_id):
    if "user" not in session:
        return redirect("/login")

    order = Order.query.get_or_404(order_id)
    if order.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    project = Project.query.get(order.project_id)
    messages = SupportMessage.query.filter_by(order_id=order_id).order_by(SupportMessage.timestamp.asc()).all()

    return render_template("order_chat.html", order=order, project=project, messages=messages)

# ---------- STUDENT SEND MESSAGE ----------
@app.route("/send_message/<int:order_id>", methods=["POST"])
def send_message(order_id):
    if "user" not in session:
        return redirect("/login")

    order = Order.query.get_or_404(order_id)
    if order.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    text = request.form["message"].strip()
    if text:
        msg = SupportMessage(order_id=order_id, sender="student", text=text)
        db.session.add(msg)
        db.session.commit()

    return redirect(f"/order_chat/{order_id}")

# ---------- ADMIN SEND MESSAGE ----------
@app.route("/admin_reply/<int:order_id>", methods=["POST"])
def admin_reply(order_id):
    if "admin" not in session:
        return redirect("/admin_login")

    text = request.form["message"].strip()
    if text:
        msg = SupportMessage(order_id=order_id, sender="admin", text=text)
        db.session.add(msg)
        db.session.commit()

    return redirect(f"/admin_chat/{order_id}")

# ---------- ADMIN CHAT VIEW ----------
@app.route("/admin_chat/<int:order_id>")
def admin_chat(order_id):
    if "admin" not in session:
        return redirect("/admin_login")

    order = Order.query.get_or_404(order_id)
    user = User.query.get(order.user_id)
    project = Project.query.get(order.project_id)
    messages = SupportMessage.query.filter_by(order_id=order_id).order_by(SupportMessage.timestamp.asc()).all()

    return render_template("admin_chat.html", order=order, user=user, project=project, messages=messages)

# ---------- CUSTOM PROJECT CHAT (Student View) ----------
@app.route("/custom_chat/<int:cp_id>")
def custom_chat(cp_id):
    if "user" not in session:
        return redirect("/login")

    cp = CustomProject.query.get_or_404(cp_id)
    if cp.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    messages = CustomMessage.query.filter_by(custom_project_id=cp_id).order_by(CustomMessage.timestamp.asc()).all()
    return render_template("custom_chat.html", cp=cp, messages=messages)

# ---------- CUSTOM PROJECT SEND MESSAGE (Student) ----------
@app.route("/custom_send/<int:cp_id>", methods=["POST"])
def custom_send(cp_id):
    if "user" not in session:
        return redirect("/login")

    cp = CustomProject.query.get_or_404(cp_id)
    if cp.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    text = request.form["message"].strip()
    if text:
        msg = CustomMessage(custom_project_id=cp_id, sender="student", text=text)
        db.session.add(msg)
        db.session.commit()

    return redirect(f"/custom_chat/{cp_id}")

# ---------- CUSTOM PROJECT ADMIN CHAT VIEW ----------
@app.route("/custom_admin_chat/<int:cp_id>")
def custom_admin_chat(cp_id):
    if "admin" not in session:
        return redirect("/admin_login")

    cp = CustomProject.query.get_or_404(cp_id)
    user = User.query.get(cp.user_id)
    messages = CustomMessage.query.filter_by(custom_project_id=cp_id).order_by(CustomMessage.timestamp.asc()).all()
    return render_template("custom_admin_chat.html", cp=cp, user=user, messages=messages)

# ---------- CUSTOM PROJECT ADMIN REPLY ----------
@app.route("/custom_admin_reply/<int:cp_id>", methods=["POST"])
def custom_admin_reply(cp_id):
    if "admin" not in session:
        return redirect("/admin_login")

    text = request.form["message"].strip()
    if text:
        msg = CustomMessage(custom_project_id=cp_id, sender="admin", text=text)
        db.session.add(msg)
        db.session.commit()

    return redirect(f"/custom_admin_chat/{cp_id}")

# ---------- ADMIN LOGIN ----------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        else:
            flash("Invalid admin credentials!", "error")

    return render_template("admin_login.html")

# ---------- CUSTOM PROJECT (Student submits idea) ----------
@app.route("/custom_project", methods=["GET", "POST"])
def custom_project():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        project = CustomProject(
            user_id=session["user"],
            title=request.form["title"],
            problem=request.form["problem"],
            objective=request.form["objective"],
            outcome=request.form["outcome"]
        )
        db.session.add(project)
        db.session.commit()
        flash("Project idea submitted successfully!", "success")
        return redirect("/dashboard")

    return render_template("custom_project.html")

# ---------- ADMIN PANEL ----------
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/admin_login")

    orders = db.session.query(Order, User, Project).join(
        User, Order.user_id == User.id
    ).join(
        Project, Order.project_id == Project.id
    ).all()

    unread = {}
    for order, user, project in orders:
        count = SupportMessage.query.filter_by(order_id=order.id, sender="student").count()
        unread[order.id] = count

    custom_projects = CustomProject.query.all()

    custom_unread = {}
    for cp in custom_projects:
        count = CustomMessage.query.filter_by(custom_project_id=cp.id, sender="student").count()
        custom_unread[cp.id] = count

    return render_template("admin.html", orders=orders, unread=unread, custom_projects=custom_projects, custom_unread=custom_unread)

# ---------- APPROVE ORDER ----------
@app.route("/approve/<int:id>")
def approve_order(id):
    if "admin" not in session:
        return redirect("/admin_login")

    order = Order.query.get_or_404(id)
    order.status = "Approved"
    user = User.query.get(order.user_id)
    db.session.commit()
    
    send_update_email(user.email, "Project Approved - ProjectMate", 
                      f"Hi {user.username}, your request for project ID {order.project_id} has been approved! You can now proceed with the payment from your dashboard.")
    
    flash("Order approved! Student can now pay.", "success")
    return redirect("/admin")

# ---------- REJECT ORDER ----------
@app.route("/reject/<int:id>")
def reject_order(id):
    if "admin" not in session:
        return redirect("/admin_login")

    order = Order.query.get_or_404(id)
    order.status = "Rejected"
    user = User.query.get(order.user_id)
    db.session.commit()
    
    send_update_email(user.email, "Project Request Update - ProjectMate", 
                      f"Hi {user.username}, unfortunately your request for project ID {order.project_id} was not approved at this time.")
    
    flash("Order rejected!", "error")
    return redirect("/admin")

# ---------- UPDATE ORDER ----------
@app.route("/update_order/<int:id>", methods=["POST"])
def update_order(id):
    if "admin" not in session:
        return redirect("/admin_login")

    order = Order.query.get_or_404(id)
    order.admin_remark = request.form["remark"]
    user = User.query.get(order.user_id)
    db.session.commit()
    
    send_update_email(user.email, "Admin Update - ProjectMate", 
                      f"Hi {user.username}, the admin has added a remark to your order: {order.admin_remark}")
    
    flash("Update sent to student!", "success")
    return redirect("/admin")

# ---------- CONFIRM PAYMENT (Admin) ----------
@app.route("/confirm_payment/<int:id>")
def confirm_payment(id):
    if "admin" not in session:
        return redirect("/admin_login")

    order = Order.query.get_or_404(id)
    order.payment_status = "Confirmed"
    user = User.query.get(order.user_id)
    db.session.commit()
    
    send_update_email(user.email, "Payment Confirmed - ProjectMate", 
                      f"Hi {user.username}, your payment for project ID {order.project_id} has been confirmed! We will deliver the final files shortly.")
    
    flash("Payment confirmed!", "success")
    return redirect("/admin")

# ---------- ACCEPT CUSTOM PROJECT (Admin sets price) ----------
@app.route("/accept_custom/<int:id>", methods=["POST"])
def accept_custom(id):
    if "admin" not in session:
        return redirect("/admin_login")

    cp = CustomProject.query.get_or_404(id)
    cp.status = "Accepted"
    cp.price = int(request.form["price"])
    user = User.query.get(cp.user_id)
    db.session.commit()
    
    send_update_email(user.email, "Custom Project Accepted - ProjectMate", 
                      f"Hi {user.username}, your custom project request '{cp.title}' has been accepted with a price of ₹{cp.price}! Please pay the 50% upfront to start.")
    
    flash("Custom project accepted with price ₹" + str(cp.price) + "!", "success")
    return redirect("/admin")

# ---------- REJECT CUSTOM PROJECT ----------
@app.route("/reject_custom/<int:id>")
def reject_custom(id):
    if "admin" not in session:
        return redirect("/admin_login")

    cp = CustomProject.query.get_or_404(id)
    cp.status = "Rejected"
    user = User.query.get(cp.user_id)
    db.session.commit()
    
    send_update_email(user.email, "Custom Project Update - ProjectMate", 
                      f"Hi {user.username}, unfortunately your custom project request '{cp.title}' was not approved.")
    
    flash("Custom project rejected!", "error")
    return redirect("/admin")

# ---------- CUSTOM PROJECT PAYMENT ----------
@app.route("/custom_payment/<int:id>", methods=["GET", "POST"])
def custom_payment(id):
    if "user" not in session:
        return redirect("/login")

    cp = CustomProject.query.get_or_404(id)
    if cp.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    if cp.status != "Accepted":
        flash("This project is not accepted yet!", "error")
        return redirect("/dashboard")

    if cp.payment_status == "Paid":
        flash("Payment already submitted!", "error")
        return redirect("/dashboard")

    half_price = cp.price // 2

    if request.method == "POST":
        cp.transaction_id = request.form["transaction_id"]
        cp.mobile_number = request.form["mobile_number"]
        cp.email = request.form["email"]
        cp.payment_status = "Paid"
        db.session.commit()
        flash("Payment details submitted successfully!", "success")
        return redirect("/dashboard")

    return render_template("custom_payment.html", cp=cp, half_price=half_price)

# ---------- CONFIRM CUSTOM PAYMENT (Admin) ----------
@app.route("/confirm_custom_payment/<int:id>")
def confirm_custom_payment(id):
    if "admin" not in session:
        return redirect("/admin_login")

    cp = CustomProject.query.get_or_404(id)
    user = User.query.get(cp.user_id)
    
    if cp.balance_payment_status == "Paid":
        cp.balance_payment_status = "Confirmed"
        cp.status = "Paid - Ready for Delivery"
        subject = "Custom Project Balance Confirmed - ProjectMate"
        body = f"Hi {user.username}, your balance payment for '{cp.title}' has been confirmed. The admin will deliver your final files shortly!"
    else:
        cp.payment_status = "Confirmed"
        cp.status = "In Development"
        subject = "Custom Project Upfront Payment Confirmed - ProjectMate"
        body = f"Hi {user.username}, your upfront payment for '{cp.title}' has been confirmed. We are starting development!"
        
    db.session.commit()
    send_update_email(user.email, subject, body)
    
    flash("Custom project payment confirmed!", "success")
    return redirect("/admin")

# ---------- SUBMIT PROJECT PROOF (Admin uploads image/video) ----------
@app.route("/submit_proof/<int:id>", methods=["POST"])
def submit_proof(id):
    if "admin" not in session:
        return redirect("/admin_login")

    cp = CustomProject.query.get_or_404(id)
    file = request.files.get("proof_file")
    if file and file.filename:
        filename = f"proof_{id}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['DELIVERIES_FOLDER'], filename))
        cp.output_file = filename
        cp.status = "Proof Submitted - Waiting for Balance"
        user = User.query.get(cp.user_id)
        db.session.commit()
        
        send_update_email(user.email, "Project Proof of Work Available - ProjectMate", 
                          f"Hi {user.username}, the admin has uploaded proof for your project '{cp.title}'. Please review it and pay the remaining balance.")
        
        flash("Project proof uploaded!", "success")
    else:
        flash("Please select a file to upload!", "error")
    return redirect("/admin")

# ---------- CUSTOM PROJECT BALANCE PAYMENT ----------
@app.route("/custom_balance_payment/<int:id>", methods=["GET", "POST"])
def custom_balance_payment(id):
    if "user" not in session:
        return redirect("/login")

    cp = CustomProject.query.get_or_404(id)
    if cp.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    if cp.status != "Delivered":
        flash("Final payment is only available after project delivery!", "error")
        return redirect("/dashboard")

    balance_price = cp.price - (cp.price // 2)

    if request.method == "POST":
        cp.balance_transaction_id = request.form["transaction_id"]
        cp.balance_payment_status = "Paid"
        db.session.commit()
        flash("Balance payment details submitted! Admin will verify.", "success")
        return redirect("/dashboard")

    return render_template("custom_balance_payment.html", cp=cp, balance_price=balance_price)

# ---------- DELIVER ORDER (Admin uploads final project file) ----------
@app.route("/deliver_order/<int:id>", methods=["POST"])
def deliver_order(id):
    if "admin" not in session:
        return redirect("/admin_login")

    order = Order.query.get_or_404(id)
    file = request.files.get("project_file")
    if file and file.filename:
        filename = f"order_{id}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['DELIVERIES_FOLDER'], filename))
        order.project_file = filename
        order.status = "Delivered"
        user = User.query.get(order.user_id)
        db.session.commit()
        
        send_update_email(user.email, "Project Files Delivered - ProjectMate", 
                          f"Hi {user.username}, your project files have been delivered! You can download them from your dashboard now.")
        
        flash("Project file delivered to student!", "success")
    else:
        flash("Please select a file to upload!", "error")
    return redirect("/admin")

# ---------- DELIVER CUSTOM PROJECT (Admin uploads final project file) ----------
@app.route("/deliver_custom/<int:id>", methods=["POST"])
def deliver_custom(id):
    if "admin" not in session:
        return redirect("/admin_login")

    cp = CustomProject.query.get_or_404(id)
    
    if cp.balance_payment_status != "Confirmed":
        flash("You can only deliver final files after the balance is confirmed!", "error")
        return redirect("/admin")

    file = request.files.get("project_file")
    if file and file.filename:
        filename = f"custom_{id}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['DELIVERIES_FOLDER'], filename))
        cp.project_file = filename
        cp.status = "Completed"
        user = User.query.get(cp.user_id)
        db.session.commit()
        
        send_update_email(user.email, "Final Project Files Delivered - ProjectMate", 
                          f"Hi {user.username}, your custom project '{cp.title}' final files have been delivered! You can download them from your dashboard now.")
        
        flash("Final project zip delivered!", "success")
    else:
        flash("Please select a file to upload!", "error")
    return redirect("/admin")

# ---------- DOWNLOAD ORDER (Student downloads project file) ----------
@app.route("/download_order/<int:id>")
def download_order(id):
    if "user" not in session:
        return redirect("/login")

    order = Order.query.get_or_404(id)
    if order.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    if order.payment_status != "Confirmed":
        flash("Payment not confirmed yet!", "error")
        return redirect("/dashboard")

    if not order.project_file:
        flash("Project file not available yet!", "error")
        return redirect("/dashboard")

    return send_from_directory(app.config['DELIVERIES_FOLDER'], order.project_file, as_attachment=True)

# ---------- DOWNLOAD CUSTOM PROJECT (Student downloads project file) ----------
@app.route("/download_custom/<int:id>")
def download_custom(id):
    if "user" not in session:
        return redirect("/login")

    cp = CustomProject.query.get_or_404(id)
    if cp.user_id != session["user"]:
        flash("Unauthorized!", "error")
        return redirect("/dashboard")

    if cp.balance_payment_status != "Confirmed":
        flash("Please pay the remaining balance and wait for admin confirmation to download the final project files!", "error")
        return redirect("/dashboard")

    if not cp.project_file:
        flash("Project file not available yet!", "error")
        return redirect("/dashboard")

    return send_from_directory(app.config['DELIVERIES_FOLDER'], cp.project_file, as_attachment=True)

# ---------- ADMIN LOGOUT ----------
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    flash("Admin logged out!", "success")
    return redirect("/admin_login")

# ---------- DATABASE CREATE ----------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if Project.query.count() == 0:
            # FRONTEND PROJECTS
            db.session.add(Project(name="Frontend Portfolio Website", price=999))
            db.session.add(Project(name="Frontend E-Learning UI", price=1499))
            db.session.add(Project(name="Frontend Admin Dashboard React", price=1999))
            db.session.add(Project(name="Frontend Job Portal UI", price=1499))
            db.session.add(Project(name="Frontend Food Delivery Website", price=1299))

            # DATA ANALYTICS PROJECTS
            db.session.add(Project(name="Analytics Sales Dashboard PowerBI", price=1999))
            db.session.add(Project(name="Analytics Student Performance Analysis", price=1499))
            db.session.add(Project(name="Analytics Customer Churn Prediction", price=2499))
            db.session.add(Project(name="Analytics Netflix Data Analysis", price=1499))
            db.session.add(Project(name="Analytics HR Employee Dashboard", price=1999))

            db.session.commit()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)