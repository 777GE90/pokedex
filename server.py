from flask import Flask
from flask_restful import Api, Resource
from http import HTTPStatus


app = Flask(__name__)
api = Api(app)


class Pokemon(Resource):
    def get(self, pokemon_name):
        pass


api.add_resource(Pokemon, "/pokemon/<string:pokemon_name>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
