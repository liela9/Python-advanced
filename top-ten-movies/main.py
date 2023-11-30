from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker

import requests
from secret import TMDB_TOKEN # access token auth for 'The Movie Data Base' website.

TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)

# Create DataBase
engine = create_engine('sqlite:///top-ten-movies/movies.db')
Base = sqlalchemy.orm.declarative_base()

# Note - We can see the DB in the DB Browser of "SQLite" that installed on our computer:
# C:\Program Files\DB Browser for SQLite.

# Create Table
class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)
    year = Column(Integer, nullable=False)
    description = Column(String(500), nullable=False)
    rating = Column(Float, nullable=True)
    ranking = Column(Integer, nullable=True)
    review = Column(String(250), nullable=True)
    img_url = Column(String(250), nullable=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class RateMovieForm(FlaskForm):
    rating = FloatField(label='Your Rating Out Of 10', validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')


class AddMovieForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


# All app routes below.
@app.route("/")
def home():
    all_movies = session.query(Movie).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    movie_id = request.args.get('id')
    movie = session.query(Movie).filter_by(id=movie_id).first()
    form = RateMovieForm()

    if form.validate_on_submit():
        rating = float(form.rating.data)
        review = form.review.data
        session.query(Movie).filter_by(id=movie_id).update({"rating":rating, "review":review})
        session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie = session.query(Movie).filter_by(id=movie_id).first()
    session.delete(movie)
    session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    add_movie_form = AddMovieForm()

    if add_movie_form.validate_on_submit():
        movie_title = add_movie_form.title.data
        url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&language=en-US&page=1"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        all_results = response.json()['results']
        if all_results == []:
            return render_template('error.html', message="Sorry, we couldn't find that movie.")    
        return render_template("select.html", all_results=all_results)
    
    from sqlalchemy import func
    rows = session.query(func.count(Movie.id)).scalar()
    if rows == 10:
        return render_template('error.html', message="Can't add more movies. You have 10 on your list.")
    return render_template("add.html", form=add_movie_form)


@app.route("/find")
def find():
    movie_id = request.args.get('id')
    url = f"{TMDB_MOVIE_URL}/{movie_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }
    movie = requests.get(url, headers=headers).json() # get the movie details from 'TMBD' website
    new_movie = Movie(
        title = movie['original_title'],
        year = movie['release_date'][:4],
        description = movie['overview'],
        img_url = f"{TMDB_IMAGE_URL}{movie['poster_path']}"
    )
    try:
        session.add(new_movie) # add the movie to our database
        session.commit()
    except:
        session.rollback()
        return render_template('error.html', message="This movie is already on your list.")
    
    # find the id of the movie that was created
    movie = session.query(Movie).filter_by(title=movie['original_title']).first()
    return redirect(url_for('edit', id=movie.id))


if __name__ == '__main__':
    app.run(debug=True)