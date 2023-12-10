from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'any-secret-key'
Bootstrap(app)

# Configure login manager that handles the common tasks of logging in, logging out, and remembering your users sessions over extended periods of time.
login_manager = LoginManager()
login_manager.init_app(app)

# Create DataBase
engine = create_engine('sqlite:///authentication/users.db')
Base = sqlalchemy.orm.declarative_base()

# NOTE: We can see the DB in the DB Browser of "SQLite" that installed on our computer:
# C:\Program Files\DB Browser for SQLite.

# Configure User Table
class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    name = Column(String(1000))

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


# All app routes below
@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password=request.form['password']

        user = session.query(User).filter_by(email=email).first()
        if user is None: # that email does not exist in the database
            # create new user
            new_user = User(
                name = name,
                email = email,
                password = generate_password_hash(password=password, 
                                                method="pbkdf2:sha256", 
                                                salt_length=8
                )
            )
            session.add(new_user)
            session.commit()
            # log in that new user
            login_user(new_user)
            return redirect(url_for('secrets', name=name))
        
        # else - that user (email) already exists in the database
        flash("That email already signed up. Log in instead.", "error")
        return redirect(url_for('login'))
    
    # if request.method == "GET":
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_email = request.form['email']
        entered_password = request.form['password']
        
        user = session.query(User).filter_by(email=entered_email).first()
        if user is None: # that email does not exist in the database
            flash("Email does not exist. Try again.", "error")
        elif check_password_hash(pwhash=user.password, password=entered_password):
            login_user(user)
            return redirect(url_for('secrets'))
        else:
            flash("Wrong password. Try again.", "error")

    # if request.method == "GET":
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory("static/files", path="cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
