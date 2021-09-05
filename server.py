from flask import Flask
from flask_restful import Api, Resource

from modules import pokeapi


app = Flask(__name__)
api = Api(app)


class Pokemon(Resource):
    def get(self, pokemon_name):
        """
        Gets the details about a specific Pokemon
        :param pokemon_name: String name of the Pokemon to get
        :return: JSON response of Pokemon data
        """
        poke = pokeapi.PokeAPIWrapper()
        result, status_code = poke.get_pokemon_species_by_name(pokemon_name)
        return result, status_code


api.add_resource(Pokemon, "/pokemon/<string:pokemon_name>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
