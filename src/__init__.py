from flask import Flask, jsonify
from flask_restx import Api, Resource

# Instantiate the app
app = Flask(__name__)
api = Api(app)

# Set config
app.config.from_object("src.config.DevelopmentConfig")


class Ping(Resource):
    def get(self):
        return {"status": "success", "message": "ping"}


api.add_resource(Ping, "/ping")
