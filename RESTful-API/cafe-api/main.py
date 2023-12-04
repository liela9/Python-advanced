from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker

import random

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)

# Create DataBase
engine = create_engine('sqlite:///RESTful-API/cafe-api/cafes.db')
Base = sqlalchemy.orm.declarative_base()

# Note - We can see the DB in the DB Browser of "SQLite" that installed on our computer:
# C:\Program Files\DB Browser for SQLite.

# Cafe TABLE Configuration
class Cafe(Base):
    __tablename__ = 'cafe'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    map_url = Column(String(500), nullable=False)
    img_url = Column(String(500), nullable=False)
    location = Column(String(250), nullable=False)
    seats = Column(String(250), nullable=False)
    has_toilet = Column(Boolean, nullable=False)
    has_wifi = Column(Boolean, nullable=False)
    has_sockets = Column(Boolean, nullable=False)
    can_take_calls = Column(Boolean, nullable=False)
    coffee_price = Column(String(100), nullable=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# HTTP GET
@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/random")
def get_random_cafe():
    cafes = session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return to_dict(random_cafe)

@app.route("/all")
def get_all_cafes():
    cafes = session.query(Cafe).all()
    return jsonify(cafes_list = [to_dict(cafe) for cafe in cafes])

@app.route("/search")
def get_cafes_by_area():
    # http://127.0.0.1:5000/search?area=<value>
    area = request.args.get('area')

    cafes = session.query(Cafe).filter_by(location=f"{area}").all()
    if cafes == []:
        return {
            "error": {
                "Not Found": "Sorry, we do not have a cafe at that location."
            }
        }
    return jsonify(cafes_list = [to_dict(cafe) for cafe in cafes])


# HTTP POST
@app.route("/add", methods=["POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),
        seats = request.form.get("seats"),
        has_toilet = request.form.get("has_toilet"),
        has_wifi = request.form.get("has_wifi"),
        has_sockets = request.form.get("has_sockets"),
        can_take_calls = request.form.get("can_take_calls"),
        coffee_price = request.form.get("coffee_price")
    )

    session.add(new_cafe)
    session.commit()

    return jsonify(
        response={
            "success": "Successfully added the new cafe."
        }
    )


# HTTP PUT/PATCH 
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    new_price = request.args.get('new_price')
    cafe = session.query(Cafe).get(id)

    if cafe:
        cafe.coffee_price = new_price
        session.commit()

        return jsonify(
            response={
                "success": "Successfully updated the new coffe price."
            }
        )

    # 404 HTTP code - resource not found
    return jsonify(
        response={
            "error": "Could not find a cafe with that id in the database."
        }
    ), 404


# HTTP DELETE
@app.route("/report-closed/<int:id>", methods=["DELETE"])
def delete_cafe(id):
    cafe = session.query(Cafe).get(id)
    
    api_key = request.args.get('api-key')
    if api_key == "TopSecretAPIKey":
        if cafe:
            session.delete(cafe)
            session.commit()

            return jsonify(
                response={
                    "success": "Successfully deleted the cafe."
                }
            )
    
        # 404 HTTP code - resource not found
        return jsonify(
            response={
                "error": "Could not find a cafe with that id in the database."
            }
        ), 404
    
    return jsonify(
        response={
            "error": "Not allowed. Make sure you have the correct API key."
        }
    ), 403


# General methods
def to_dict(cafe:Cafe):
    return {
        "id":cafe.id,
        "name":cafe.name,
        "map_url":cafe.map_url,
        "img_url":cafe.img_url,
        "location":cafe.location,
        "seats":cafe.seats,
        "has_toilet":cafe.has_toilet,
        "has_wifi":cafe.has_wifi,
        "has_sockets":cafe.has_sockets,
        "can_take_calls":cafe.can_take_calls,
        "coffee_price":cafe.coffee_price
    }


if __name__ == '__main__':
    app.run(debug=True)
