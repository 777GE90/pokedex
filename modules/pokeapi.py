import os
import requests

from http import HTTPStatus


class PokeAPIWrapper:
    # The URL of the Pokeapi, including the inital API path
    POKEAPI_URL = os.environ.get("POKEAPI_URL", None)
    # Set the maximum timeout time of every request
    REQUEST_TIMEOUT_TIME = 10

    def __init__(self):
        """
        Initialise the wrapper
        """
        if PokeAPIWrapper.POKEAPI_URL is None:
            raise RuntimeError(
                "Missing required environment variable 'POKEAPI_URL'"
            )

    def _build_pokeapi_url(self, path):
        """
        Given a path, builds the Pokeapi.co URL
        :param path: String API path to target
        :return: String full URL to target
        """
        if path.startswith("/"):
            return f"{PokeAPIWrapper.POKEAPI_URL}{path}"
        return f"{PokeAPIWrapper.POKEAPI_URL}/{path}"

    def _send_pokeapi_get(self, path):
        """
        A generic method to send GET requests to Pokeapi.co
        :param path: String target path to hit on the API
        :return: A Tuple containing:
        - Dict of the response data
        - Integer HTTP Status Code
        """
        result = {}
        url = self._build_pokeapi_url(path)
        try:
            response = requests.get(
                url,
                timeout=PokeAPIWrapper.REQUEST_TIMEOUT_TIME,
            )
            if response.status_code != HTTPStatus.OK:
                result["message"] = f"Error: {response.text}"
                return result, response.status_code

            result = response.json()
            return result, response.status_code
        except requests.exceptions.RequestException:
            result[
                "message"
            ] = "Error: Failed to retrieve data, please try again later"
        except Exception:
            result[
                "message"
            ] = "Error: Bad response received from remote server"
        return result, HTTPStatus.INTERNAL_SERVER_ERROR

    def get_pokemon_species_by_id(self, species_id):
        """
        Given a Pokemon Species ID, gets the details about that Pokemon species
        :param species_id: Integer ID of the species
        :return: A Tuple containing:
        - Dict of the response data
        - Integer HTTP Status Code
        """
        pokemon_species_data = {}
        result, status_code = self._send_pokeapi_get(
            f"/pokemon-species/{species_id}/"
        )
        if status_code != HTTPStatus.OK:
            return result, status_code

        try:
            pokemon_species_data["name"] = result["name"]
            pokemon_species_data["habitat"] = result["habitat"]["name"]
            pokemon_species_data["isLegendary"] = result["is_legendary"]
            pokemon_species_data["description"] = (
                result["flavor_text_entries"][0]["flavor_text"]
                .replace("\n", " ")
                .replace("\r", " ")
                .replace("\f", " ")
            )
        except Exception:
            return {
                "message": "Error: Failed to parse data"
            }, HTTPStatus.INTERNAL_SERVER_ERROR

        return pokemon_species_data, HTTPStatus.OK

    def get_pokemon_species_by_name(self, pokemon_name):
        """
        Given a Pokemon name, gets the details about that Pokemon species
        :param pokemon_name: String name of the Pokemon
        :return: A Tuple containing:
        - Dict of the response data
        - Integer HTTP Status Code
        """
        result, status_code = self._send_pokeapi_get(
            f"/pokemon/{pokemon_name}"
        )
        if status_code != HTTPStatus.OK:
            return result, status_code

        try:
            species_url = result["species"]["url"]
            species_id = int(species_url.split("/")[-2])
            return self.get_pokemon_species_by_id(species_id)
        except Exception:
            return {
                "message": "Error: Failed to parse data"
            }, HTTPStatus.INTERNAL_SERVER_ERROR
