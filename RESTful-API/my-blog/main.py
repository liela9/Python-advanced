from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker

import datetime


CURRENT_YEAR = datetime.date.today().year

app = Flask(__name__)
ckeditor = CKEditor(app) # text editor
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6a'
Bootstrap(app)

# Create DataBase
engine = create_engine('sqlite:///RESTful-API/my-blog/posts.db')
Base = sqlalchemy.orm.declarative_base()

# NOTE: We can see the DB in the DB Browser of "SQLite" that installed on our computer:
# C:\Program Files\DB Browser for SQLite.

# Configure BlogPost Table
class BlogPost(Base):
    __tablename__ = 'blog_post'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True, nullable=False)
    subtitle = Column(String(250), nullable=False)
    date = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(250), nullable=False)
    img_url = Column(String(250), nullable=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# WTForms - Configure CreatePostForm form
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")



# All app routes below
# GET HTTP
@app.route('/')
def home():
    posts = session.query(BlogPost).all()
    return render_template("index.html", posts=posts, year=CURRENT_YEAR)

@app.route('/about')
def about():
    return render_template("about.html", year=CURRENT_YEAR)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = session.query(BlogPost).get(post_id)
    return render_template("post.html", post=post, year=CURRENT_YEAR)


# POST HTTP
@app.route('/contact', methods=["POST", "GET"])
def contact():
    if request.method == 'GET':
        return render_template("contact.html", year=CURRENT_YEAR, msg_sent=False)
    return render_template("contact.html", year=CURRENT_YEAR, msg_sent=True)

@app.route('/new-post', methods=["POST", "GET"])
def create_post():
    form = CreatePostForm()

    if request.method == 'POST' and form.validate_on_submit():
        month_name = datetime.date.today().strftime('%B')
        date_numbet = datetime.date.today().strftime('%d')

        new_post = BlogPost(
            title = request.form.get("title"),
            subtitle = request.form.get("subtitle"),
            date = f"{month_name} {date_numbet}, {CURRENT_YEAR}",
            body = request.form.get("body"),
            author = request.form.get("author"),
            img_url = request.form.get("img_url")
        )
        session.add(new_post)
        session.commit()
        return redirect(url_for('home'))
    return render_template("make-post.html", form=form, is_edit = False)

@app.route('/edit-post/<int:post_id>', methods=["POST", "GET"])
def edit_post(post_id):
    post = session.query(BlogPost).get(post_id)

    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        author=post.author,
        img_url=post.img_url
    )

    if request.method == 'POST' and edit_form.validate_on_submit():
        post.title = request.form.get("title")
        post.subtitle = request.form.get("subtitle")
        post.body = request.form.get("body")
        post.author = request.form.get("author")
        post.img_url = request.form.get("img_url")
        session.commit()
        return redirect(url_for('view_post', post_id=post_id))

    return render_template("make-post.html", form=edit_form, is_edit = True)

@app.route('/delete/<int:post_id>', methods=["POST", "GET"])
def delete_post(post_id):
    session.query(BlogPost).filter_by(id=post_id).delete()
    session.commit()
    return redirect(url_for('home'))

# NOTE: HTML forms do not accept PUT, PATCH or DELETE methods. So while the last two methods would normally be a PUT/DELETE requests, because the request is coming from a HTML form, we define them as a POST requests.


if __name__ == "__main__":
    app.run(debug=True)