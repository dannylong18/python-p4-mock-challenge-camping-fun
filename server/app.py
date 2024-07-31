#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():

    if request.method == 'GET':
        campers = [camper.to_dict(rules=("-signups",)) for camper in Camper.query.all()]
        return make_response(campers, 200)
    
    elif request.method == 'POST':
        json = request.get_json()

        name = json.get('name')
        age = json.get('age')
        
        # errors = {}

        # if not name:
        #     errors['name'] = 'name must be present'

        # if not age:
        #     errors['age'] = 'age must be an integer between 8 and 18'

        # if errors:
        #     return {'errors': errors} , 400
        
        # new_camper = Camper(
        #     name = name,
        #     age = age
        # )
        
        # db.session.add(new_camper)
        # db.session.commit()

        # return make_response(new_camper.to_dict(), 201)

        errors = []

        if not name:
            errors.append('Name must be present.')
        
        try:
            age = int(age)
        except (TypeError, ValueError):
            errors.append('Age must be an integer.')
        
        if not (8 <= age <= 18):
            errors.append('Age must be an integer between 8 and 18.')

        if errors:
            return jsonify({'errors': errors}), 400
        
        new_camper = Camper(name=name, age=age)
        
        try:
            db.session.add(new_camper)
            db.session.commit()
        except ValueError as e:
            return jsonify({'errors': [str(e)]}), 400

        return make_response(new_camper.to_dict(), 201)
        
@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):

    camper = Camper.query.filter(Camper.id == id).first()

    if request.method == 'GET':
        if not camper:
            return {'error': 'Camper not found'}, 404
        
        camper_dict = camper.to_dict()
        return make_response(camper_dict, 200)
        
    
    elif request.method == 'PATCH':
        if not camper:
            return {'error': 'Camper not found'}, 404
        
        # for attr in request.form:
        #     setattr(camper, attr, request.form.get(attr))
        json = request.get_json()

        name = json.get('name')
        age = json.get('age')

        errors = []

        if name is not None or '':
            try:
                camper.name = name
            except ValueError:
                errors.append('validation errors')

        if age is not None:
            try:
                camper.age = int(age)
            except ValueError:
                errors.append('validation errors')
        try:
            db.session.add(camper)
            db.session.commit()

        except ValueError as e:
            return jsonify({'errors': [str(e)]}), 400
        
        if errors:
            return {'errors': errors} , 400

        camper_dict = camper.to_dict()
        resp = make_response(camper_dict, 202)
        return resp
        
@app.route('/activities', methods=['GET'])
def get_activities():
    activities = [activity.to_dict() for activity in Activity.query.all()]
    return make_response(activities, 200)

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if not activity:
        return {'error': 'Activity not found'}, 404
    
    if request.method == 'DELETE':
        db.session.delete(activity)
        db.session.commit()
        return {}, 204

@app.route('/signups', methods=['POST'])
def create_signup():
    json = request.get_json()

    camper_id = json.get('camper_id')
    activity_id = json.get('activity_id')
    time = json.get('time')

    errors = []

    if time is None or not (0<=time<=23):
        errors.append("validation errors")
    
    if errors:
        return {'errors': errors}, 400
    
    new_signup = Signup(
        time = time,
        activity_id = activity_id,
        camper_id = camper_id
    )

    db.session.add(new_signup)
    db.session.commit()

    new_signup_dict = new_signup.to_dict()
    
    new_signup_dict['activity'] = Activity.query.filter(Activity.id == activity_id).first().to_dict()
    new_signup_dict['camper'] = Camper.query.filter(Camper.id == camper_id).first().to_dict()

    

    resp = make_response(new_signup_dict, 201)
    return resp



if __name__ == '__main__':
    app.run(port=5555, debug=True)
