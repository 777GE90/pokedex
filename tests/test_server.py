import unittest

from server import app


class PokemonTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.app = app.test_client()

    def test_good_request(self):
        """
        Assert an HTTP 200 response from the server and that the required
        params exist in the response
        """
        response = self.app.get("/pokemon/mewtwo")
        self.assertEqual(response.status_code, 200)

        pokemon_json = response.json()
        self.assertIn("name", pokemon_json)
        self.assertIn("is_legendary", pokemon_json)
        self.assertIn("description", pokemon_json)
        self.assertIn("habitat", pokemon_json)
