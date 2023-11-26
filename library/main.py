from flask import Flask, render_template, request
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Create DataBase
engine = create_engine('sqlite:///library/my-books-collection.db')
Base = sqlalchemy.orm.declarative_base()

# Note - We can see the DB in the DB Browser of "SQLite" that installed on our computer.

# Create Table
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True, nullable=False)
    author = Column(String(250), nullable=False)
    parts = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

with open("library/id.txt", mode="r") as file:
    counter = int(file.read())


@app.route('/')
def home():
    all_books = session.query(Book).all()
    return render_template('index.html', all_books=all_books)

@app.route("/add", methods=['GET', 'POST'])
def add():
    global counter

    if request.method == "POST":
        try:
            counter += 1
            # save the last used 'id' for next running.
            with open("library/id.txt", mode="w") as file:
                file.write(f"{counter}")

            new_book = Book(id=counter, title=request.form['title'], author=request.form['author'], parts=request.form['parts'],rating=request.form['rating'])
            session.add(new_book)
            session.commit()
            all_books = session.query(Book).all()
            return render_template('index.html', all_books=all_books)
        except:
            return render_template('error.html', message="This book already exists in your library.")
    return render_template('add.html')

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    book = session.query(Book).filter_by(id=request.args.get('id')).first()

    if request.method == "POST":
        try:
            book.rating = request.form['new_rating']
            session.commit()
            all_books = session.query(Book).all()
            return render_template('index.html', all_books=all_books)
        except:
            return render_template('error.html', message="Rating must be a number.")
    
    return render_template('edit.html', book=book)

@app.route("/delete")
def delete():
    book_id = request.args.get('id')
    book = session.query(Book).filter_by(id=book_id).first()
    session.delete(book)
    session.commit()
    all_books = session.query(Book).all()
    return render_template('index.html', all_books=all_books)

@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == "__main__":
    app.run(debug=True)
