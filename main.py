import sqlalchemy
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy.orm import Session

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


# # Create the movies table in the database
# with app.app_context():
#     db.create_all()


def get_random_cafe():
    with app.app_context():
        cafes_num = db.session.query(Cafe).count()
        random_db_cafe_id = random.randint(0, cafes_num)
        random_cafe = Cafe.query.filter_by(id=random_db_cafe_id).first()

    return random_cafe


def add_cafe():
    with app.app_context():
        new_cafe = Cafe()
        db.session.add(new_cafe)
        db.session.commit()


def update_price(cafe_id, new_price):
    with app.app_context():
        cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
        cafe_to_update.coffee_price = new_price
        db.session.commit()


def delete_cafe(cafe_id):
    with app.app_context():
        cafe_to_delete = Cafe.query.filter_by(id=cafe_id).first()
        db.session.delete(cafe_to_delete)
        db.session.commit()


def cafe_dictionary(random_cafe):
    return {
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
        "has_sockets": random_cafe.has_sockets,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "id": random_cafe.id,
        "img_url": random_cafe.img_url,
        "loc": random_cafe.location,
        "map_url": random_cafe.map_url,
        "name": random_cafe.name,
        "seats": random_cafe.seats,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def show_random_cafe():
    random_cafe = get_random_cafe()
    return jsonify(cafe=cafe_dictionary(random_cafe))


@app.route("/all", methods=["GET"])
def show_all_cafes():
    cafes = Cafe.query.all()
    all_cafes = {}
    for cafe in cafes:
        all_cafes[f"{cafe.name} "] = cafe_dictionary(cafe)
    return jsonify(all_cafes=all_cafes)


@app.route("/search", methods=["GET"])
def show_region_cafes():
    location = request.args.get("loc")
    cafes = Cafe.query.all()
    region_cafes = {}
    for cafe in cafes:
        if cafe.location == location:
            region_cafes[f"{cafe.name} "] = cafe_dictionary(cafe)

    if region_cafes == {}:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    else:
        return jsonify(cafes=region_cafes)


@app.route("/add", methods=["POST"])
def add_new_cafe():
    if request.method == "POST":
        return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update_price/<int:coffee_id>", methods=["PATCH"])
def update_coffee_price(coffee_id):
    if request.method == "PATCH":
        new_price = request.args.get("new_price")
        try:
            update_price(coffee_id, new_price)
        except AttributeError:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."})
        else:
            return jsonify(response={"success": "Successfully updated the price."})


@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_existing_cafe(cafe_id):
    if request.method == "DELETE":
        api_key = request.args.get("api_key")
        if api_key == "TopSecretAPIKey":
            try:
                delete_cafe(cafe_id)
            except sqlalchemy.orm.exc.UnmappedInstanceError:
                return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."})
            else:
                return jsonify(response={"success": "Successfully deleted the specified cafe."})
        else:
            return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key.")


if __name__ == '__main__':
    app.run(debug=True)
