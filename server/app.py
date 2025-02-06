#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from werkzeug.exceptions import NotFound

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app, origins="*")
migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]

        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
             is_in_stock=data['is_in_stock'] 
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)

        
api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()

        if plant is not None:
            return make_response(jsonify(plant), 200)
        
        return make_response(jsonify({"error": "Plant not found"}), 404)
    
    def patch(self, id):
        record = Plant.query.filter_by(id=id).first()
        if record is None:
            return {"error": "Record not found"}, 404

        data = request.get_json()
        for key, value in data.items():
             setattr(record, key, value)
        
        db.session.add(record)
        db.session.commit()

        response_dict = record.to_dict()

        response = make_response(jsonify(response_dict), 200)

        response.headers["Content-Type"] = "application/json"

        return response
    
    def delete(self, id):
        record = Plant.query.filter_by(id=id).first()

        if record is None:
            return {"error": "Plant not found"}, 404
        
        db.session.delete(record)
        db.session.commit()

        return '', 204

api.add_resource(PlantByID, '/plants/<int:id>')

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(jsonify({"error": "This resource is not found in the server"}, e), 404)
    return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)