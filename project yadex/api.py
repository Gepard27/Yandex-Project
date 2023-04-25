from flask import jsonify
from flask_restful import  abort, Api, Resource
from data import db_session
from data.joke import Joke


class JokeResource(Resource):
    def get(self, id):
        session = db_session.create_session()
        joke = session.query(Joke).get(id)
        if not joke:
            abort(404, message=f'Joke {id} not found')
        return jsonify(joke.to_dict(only=('title', 'text', 'user_id')))


class JokeListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jokes = session.query(Joke).all()
        return jsonify([item.to_dict(only=('title', 'text', 'user_id')) for item in jokes])
