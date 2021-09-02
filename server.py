from flask import Flask
from flask_restful import Api, Resource
from http import HTTPStatus


app = Flask(__name__)
api = Api(app)


class Index(Resource):
    def get(self):
        return (
            {"message": "It works!"},
            HTTPStatus.OK,
        )


api.add_resource(Index, "/")


if __name__ != "__main__":
    print("A")


if __name__ == "__main__":
    print("B")
    app.run(host="0.0.0.0", port=5000)
