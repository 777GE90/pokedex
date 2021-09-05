import unittest

from unittest.mock import patch
from requests.exceptions import ConnectTimeout

from tests import mock_data
from modules.pokeapi import PokeAPIWrapper


class TestPokeAPIWrapper(unittest.TestCase):
    def setUp(self):
        self.poke = PokeAPIWrapper()

    def test_build_pokeapi_url(self):
        """
        Tests the Pokeapi URL is built correctly
        """
        url = self.poke._build_pokeapi_url("/pokemon/test")
        self.assertEqual(url, f"{PokeAPIWrapper.POKEAPI_URL}/pokemon/test")
        url = self.poke._build_pokeapi_url("pokemon/test")
        self.assertEqual(url, f"{PokeAPIWrapper.POKEAPI_URL}/pokemon/test")

    @patch("requests.get")
    def test_send_pokeapi_get_404(self, mock_get):
        """
        Tests the correct response is given when a 404 is returned
        """
        mock_get.return_value.status_code = 404
        mock_get.return_value.text = "Not Found"
        result, status = self.poke._send_pokeapi_get("/pokemon/test")
        self.assertEqual(result["message"], "Error: Not Found")
        self.assertEqual(status, 404)

    @patch("requests.get")
    def test_send_pokeapi_get_exception(self, mock_get):
        """
        Tests the correct response is given when an exception is raised
        """
        mock_get.side_effect = ConnectTimeout
        result, status = self.poke._send_pokeapi_get("/pokemon/test")
        self.assertEqual(
            result["message"],
            "Error: Failed to retrieve data, please try again later",
        )
        self.assertEqual(status, 500)

    @patch("requests.get")
    def test_send_pokeapi_bad_data(self, mock_get):
        """
        Tests the correct response is given when bad data is received from the
        API
        """
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = Exception
        result, status = self.poke._send_pokeapi_get("/pokemon/test")
        self.assertEqual(
            result["message"],
            "Error: Bad response received from remote server",
        )
        self.assertEqual(status, 500)

    @patch("requests.get")
    def test_send_pokeapi_get_success(self, mock_get):
        """
        Tests the correct response is given when a good request is made
        """
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_data.get_mewtwo
        result, status = self.poke._send_pokeapi_get("/pokemon/mewtwo")
        self.assertEqual(result, mock_data.get_mewtwo)
        self.assertEqual(status, 200)

    @patch("modules.pokeapi.PokeAPIWrapper._send_pokeapi_get")
    def test_get_pokemon_species_by_name_bad_api_response(self, mock_send_get):
        """
        Tests getting a pokemon returns the correct response when the API
        fails
        """
        send_pokeapi_get_response = {"message": "Error: Not Found"}
        mock_send_get.return_value = send_pokeapi_get_response, 404
        result, status = self.poke.get_pokemon_species_by_name("mewtwo")
        self.assertEqual(result, send_pokeapi_get_response)
        self.assertEqual(status, 404)

    @patch("modules.pokeapi.PokeAPIWrapper._send_pokeapi_get")
    def test_get_pokemon_species_by_name_invalid_data(self, mock_send_get):
        """
        Tests getting a pokemon returns the correct response when the API data
        is not as expected
        """
        send_pokeapi_get_response = {"base_experience": 306}
        mock_send_get.return_value = send_pokeapi_get_response, 200
        result, status = self.poke.get_pokemon_species_by_name("mewtwo")
        self.assertEqual(result["message"], "Error: Failed to parse data")
        self.assertEqual(status, 500)

    @patch("modules.pokeapi.PokeAPIWrapper.get_pokemon_species_by_id")
    @patch("modules.pokeapi.PokeAPIWrapper._send_pokeapi_get")
    def test_get_pokemon_species_by_name_good(
        self, mock_send_get, mock_get_species
    ):
        """
        Tests getting a pokemon returns a good response
        """
        mock_send_get.return_value = mock_data.get_mewtwo, 200
        mock_get_species.return_value = {
            "name": "mewtwo",
            "habitat": "rare",
            "isLegendary": True,
            "description": "Some description",
        }, 200
        result, status = self.poke.get_pokemon_species_by_name("mewtwo")
        self.assertEqual(result["name"], "mewtwo")
        self.assertEqual(result["habitat"], "rare")
        self.assertEqual(result["isLegendary"], True)
        self.assertEqual(result["description"], "Some description")
        self.assertEqual(status, 200)

    @patch("modules.pokeapi.PokeAPIWrapper._send_pokeapi_get")
    def test_get_pokemon_species_by_id_bad_api_response(self, mock_send_get):
        """
        Tests getting a pokemon species returns the correct response when the
        API fails
        """
        send_pokeapi_get_response = {"message": "Error: Not Found"}
        mock_send_get.return_value = send_pokeapi_get_response, 404
        result, status = self.poke.get_pokemon_species_by_id(150)
        self.assertEqual(result, send_pokeapi_get_response)
        self.assertEqual(status, 404)

    @patch("modules.pokeapi.PokeAPIWrapper._send_pokeapi_get")
    def test_get_pokemon_species_by_id_invalid_data(self, mock_send_get):
        """
        Tests getting a pokemon species returns the correct response when the
        API data is not as expected
        """
        send_pokeapi_get_response = {"capture_rate": 3}
        mock_send_get.return_value = send_pokeapi_get_response, 200
        result, status = self.poke.get_pokemon_species_by_id(150)
        self.assertEqual(result["message"], "Error: Failed to parse data")
        self.assertEqual(status, 500)

    @patch("modules.pokeapi.PokeAPIWrapper._send_pokeapi_get")
    def test_get_pokemon_species_by_id_good(self, mock_send_get):
        """
        Tests getting a pokemon species returns a good response
        """
        mock_send_get.return_value = mock_data.get_mewtwo_species, 200
        result, status = self.poke.get_pokemon_species_by_id(150)
        self.assertEqual(result["name"], "mewtwo")
        self.assertEqual(result["habitat"], "rare")
        self.assertEqual(result["isLegendary"], True)
        self.assertEqual(
            result["description"],
            mock_data.get_mewtwo_species["flavor_text_entries"][0][
                "flavor_text"
            ],
        )
        self.assertEqual(status, 200)
