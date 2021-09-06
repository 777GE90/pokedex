from http import HTTPStatus
from flask import Flask
from flask_restful import Api, Resource

from modules import pokeapi, funtranslations


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


class PokemonTranslated(Resource):
    def get(self, pokemon_name):
        """
        Gets the translated Pokemon description and basic information
        """
        poke = pokeapi.PokeAPIWrapper()
        p_result, p_status_code = poke.get_pokemon_species_by_name(
            pokemon_name
        )
        # Attempt to translate description if possible
        if p_status_code == HTTPStatus.OK:
            translate = funtranslations.FunTranslationsAPIWrapper()
            if (
                p_result["habitat"].lower() == "cave"
                or p_result["isLegendary"]
            ):
                t_result, t_status_code = translate.translate_yoda(
                    p_result["description"]
                )
            else:
                t_result, t_status_code = translate.translate_shakespeare(
                    p_result["description"]
                )
            if t_status_code == HTTPStatus.OK:
                p_result["description"] = t_result["translation"]
        return p_result, p_status_code


api.add_resource(Pokemon, "/pokemon/<string:pokemon_name>")
api.add_resource(
    PokemonTranslated, "/pokemon/translated/<string:pokemon_name>"
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
