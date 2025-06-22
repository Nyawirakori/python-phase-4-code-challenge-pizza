#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# @app.route("/")
# def index():
#     return "<h1>Code challenge</h1>"

class Home(Resource):
    def get(self):
        return make_response("Code challenge", 200)
    
api.add_resource(Home, '/')

#GET Restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(restaurants, 200)
        
api.add_resource(Restaurants, '/restaurants')

class RestaurantsById(Resource):
    #Getting Restaurants by id
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return make_response(restaurant.to_dict_with_pizzas(), 200)
        return make_response({"error": "Restaurant not found"}, 404)

     #Deleting restaurants by id
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()

            return make_response(f'{restaurant.name} was deleted successfully, 200')
        return make_response({"error":"Restaurant not found"}, 404)
    
api.add_resource(RestaurantsById, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict_all_pizzas() for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)
    
api.add_resource(Pizzas, '/pizzas')

#creating a new RestaurantPizza(POST)
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:

            new_rp = RestaurantPizza(
                price=data.get("price"),
                pizza_id=data.get("pizza_id"),
                restaurant_id=data.get("restaurant_id")
            )

            db.session.add(new_rp)
            db.session.commit()

            # build response structure
            response = {
                "id": new_rp.id,
                "price": new_rp.price,
                "pizza_id": new_rp.pizza_id,
                "restaurant_id": new_rp.restaurant_id,
                "pizza": {
                    "id": new_rp.pizza.id,
                    "name": new_rp.pizza.name,
                    "ingredients": new_rp.pizza.ingredients
                },
                "restaurant": {
                    "id": new_rp.restaurant.id,
                    "name": new_rp.restaurant.name,
                    "address": new_rp.restaurant.address
                }
            }

            return make_response(response, 201)

        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)
        
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
