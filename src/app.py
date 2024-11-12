"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# [GET] /people - Get a list of all the people
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([person.to_dict() for person in people])

# [GET] /people/<int:people_id> - Get one single person's information
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify(person.to_dict())

# [GET] /planets - Get a list of all the planets
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.to_dict() for planet in planets])

# [GET] /planets/<int:planet_id> - Get one single planet's information
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.to_dict())

# [GET] /users - Get a list of all the blog post users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# [GET] /users/favorites - Get all the favorites that belong to the current user
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    # Assuming the "current user" is user with id=1 for simplicity
    user = User.query.get(1)
    return jsonify([favorite.to_dict() for favorite in user.favorites])

# [POST] /favorite/planet/<int:planet_id> - Add a new favorite planet
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # Assuming the "current user" is user with id=1 for simplicity
    favorite = Favorite(user_id=1, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.to_dict()), 201

# [POST] /favorite/people/<int:people_id> - Add new favorite people
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    favorite = Favorite(user_id=1, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.to_dict()), 201

# [DELETE] /favorite/planet/<int:planet_id> - Delete a favorite planet
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    favorite = Favorite.query.filter_by(user_id=1, planet_id=planet_id).first_or_404()
    db.session.delete(favorite)
    db.session.commit()
    return '', 204

# [DELETE] /favorite/people/<int:people_id> - Delete a favorite person
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    favorite = Favorite.query.filter_by(user_id=1, people_id=people_id).first_or_404()
    db.session.delete(favorite)
    db.session.commit()
    return '', 204

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
