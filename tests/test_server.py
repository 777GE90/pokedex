import unittest

from unittest.mock import patch
from server import app


class PokemonTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.app = app.test_client()

    @patch("modules.pokeapi.PokeAPIWrapper.get_pokemon_species_by_name")
    def test_pokemon_get(self, mock_get_pokemon):
        """
        Assert the GET Pokemon endpoint always returns the same result as the
        get_pokemon_species_by_name method
        """
        result = {
            "name": "mewtwo",
            "habitat": "rare",
            "isLegendary": True,
            "description": "Some description",
        }
        status_code = 200
        mock_get_pokemon.return_value = (result, status_code)
        response = self.app.get("/pokemon/mewtwo")
        self.assertEqual(response.status_code, 200)
        pokemon_json = response.json
        self.assertEqual(pokemon_json, result)

        result = {"message": "Error: Not Found"}
        status_code = 404
        mock_get_pokemon.return_value = (result, status_code)
        response = self.app.get("/pokemon/mewtwo")
        self.assertEqual(response.status_code, 404)
        pokemon_json = response.json
        self.assertEqual(pokemon_json, result)

    @patch(
        "modules.funtranslations.FunTranslationsAPIWrapper."
        "translate_shakespeare"
    )
    @patch("modules.funtranslations.FunTranslationsAPIWrapper.translate_yoda")
    @patch("modules.pokeapi.PokeAPIWrapper.get_pokemon_species_by_name")
    def test_pokemon_translated_get_bad_status(
        self, mock_get_pokemon, mock_yoda, mock_shakespeare
    ):
        """
        Tests that translation is not attempted when getting the Pokemon failed
        """
        result = {"message": "Error: Not Found"}
        status_code = 404
        mock_get_pokemon.return_value = (result, status_code)
        response = self.app.get("/pokemon/translated/mewtwo")
        mock_yoda.assert_not_called()
        mock_shakespeare.assert_not_called()
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.json, result)

    @patch(
        "modules.funtranslations.FunTranslationsAPIWrapper."
        "translate_shakespeare"
    )
    @patch("modules.funtranslations.FunTranslationsAPIWrapper.translate_yoda")
    @patch("modules.pokeapi.PokeAPIWrapper.get_pokemon_species_by_name")
    def test_pokemon_translated_get_correct_translator(
        self, mock_get_pokemon, mock_yoda, mock_shakespeare
    ):
        """
        Tests that the correct translator is used depending on the get_pokemon
        response
        """
        poke_result = {
            "name": "mewtwo",
            "habitat": "rare",
            "isLegendary": True,
            "description": "hello, world",
        }
        poke_status_code = 200
        mock_get_pokemon.return_value = (poke_result, poke_status_code)
        yoda_result = {
            "translation": "Force be with you,World",
        }
        yoda_status_code = 200
        mock_yoda.return_value = (yoda_result, yoda_status_code)
        response = self.app.get("/pokemon/translated/mewtwo")
        mock_yoda.assert_called()
        mock_shakespeare.assert_not_called()
        poke_result["description"] = yoda_result["translation"]
        self.assertEqual(response.status_code, poke_status_code)
        self.assertEqual(response.json, poke_result)

        poke_result = {
            "name": "mewtwo",
            "habitat": "rare",
            "isLegendary": False,
            "description": "hello, world",
        }
        poke_status_code = 200
        mock_get_pokemon.return_value = (poke_result, poke_status_code)
        shakespeare_result = {
            "translation": "Valorous morrow to thee,  sir,  ordinary",
        }
        shakespeare_status_code = 200
        mock_shakespeare.return_value = (
            shakespeare_result,
            shakespeare_status_code,
        )
        response = self.app.get("/pokemon/translated/mewtwo")
        mock_shakespeare.assert_called()
        poke_result["description"] = shakespeare_result["translation"]
        self.assertEqual(response.status_code, shakespeare_status_code)
        self.assertEqual(response.json, poke_result)

    @patch("modules.funtranslations.FunTranslationsAPIWrapper.translate_yoda")
    @patch("modules.pokeapi.PokeAPIWrapper.get_pokemon_species_by_name")
    def test_pokemon_translated_get_ft_failure(
        self, mock_get_pokemon, mock_yoda
    ):
        """
        Tests that the default description is returned if the Fun Translation
        fails for whatever reason
        """
        poke_result = {
            "name": "mewtwo",
            "habitat": "rare",
            "isLegendary": True,
            "description": "hello, world",
        }
        poke_status_code = 200
        mock_get_pokemon.return_value = (poke_result, poke_status_code)
        yoda_result = {
            "message": "Error: It broke!",
        }
        yoda_status_code = 500
        mock_yoda.return_value = (yoda_result, yoda_status_code)
        response = self.app.get("/pokemon/translated/mewtwo")
        mock_yoda.assert_called()
        self.assertEqual(response.status_code, poke_status_code)
        self.assertEqual(response.json, poke_result)
