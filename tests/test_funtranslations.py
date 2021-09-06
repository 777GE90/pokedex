from http import HTTPStatus
import unittest

from unittest.mock import patch, call
from requests.exceptions import ConnectTimeout

from tests import mock_data
from modules.funtranslations import (
    FunTranslationsAPIWrapper,
    TranslationLanguage,
)


class TestFunTranslationsAPIWrapper(unittest.TestCase):
    def setUp(self):
        self.translate = FunTranslationsAPIWrapper()

    def test_build_fun_translations_url(self):
        """
        Tests the Fun Translations URL is built correctly
        """
        url = self.translate._build_fun_translator_url("/yoda.json")
        self.assertEqual(
            url, f"{FunTranslationsAPIWrapper.FUNTRANSLATIONS_URL}/yoda.json"
        )
        url = self.translate._build_fun_translator_url("yoda.json")
        self.assertEqual(
            url, f"{FunTranslationsAPIWrapper.FUNTRANSLATIONS_URL}/yoda.json"
        )

    @patch("requests.get")
    def test_send_fun_translator_get_429(self, mock_get):
        """
        Tests the correct response is given when a 429 is returned
        """
        params = {"text": "hello, world"}
        mock_get.return_value.status_code = 429
        mock_get.return_value.json.return_value = mock_data.ft_code_429
        result, status = self.translate._send_fun_translator_get(
            "/shakespeare.json", params=params
        )
        expected_msg = mock_data.ft_code_429["error"]["message"]
        self.assertEqual(result["message"], f"Error: {expected_msg}")
        self.assertEqual(status, 429)

    @patch("requests.get")
    def test_send_fun_translator_get_exception(self, mock_get):
        """
        Tests the correct response is given when an exception is raised
        """
        params = {"text": "hello, world"}
        mock_get.side_effect = ConnectTimeout
        result, status = self.translate._send_fun_translator_get(
            "/shakespeare.json", params=params
        )
        self.assertEqual(
            result["message"],
            "Error: Failed to retrieve data, please try again later",
        )
        self.assertEqual(status, 500)

    @patch("requests.get")
    def test_send_fun_translator_get_bad_data(self, mock_get):
        """
        Tests the correct response is given when bad data is received from the
        API
        """
        params = {"text": "hello, world"}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = Exception
        result, status = self.translate._send_fun_translator_get(
            "/shakespeare.json", params=params
        )
        self.assertEqual(
            result["message"],
            "Error: Bad response received from remote server",
        )
        self.assertEqual(status, 500)

    @patch("requests.get")
    def test_send_fun_translator_get_success(self, mock_get):
        """
        Tests the correct response is given when a good request is made
        """
        params = {"text": "hello, world"}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = (
            mock_data.ft_translate_hello_world
        )
        result, status = self.translate._send_fun_translator_get(
            "/shakespeare.json", params=params
        )
        self.assertEqual(result, mock_data.ft_translate_hello_world)
        self.assertEqual(status, 200)

    def test_translate_bad_translation_lang(self):
        """
        Tests a bad request response is given when a incorrect translation
        language is provided
        """
        text_2_translate = "hello, world"
        lang = "I'M THE WRONG THING"
        result, status = self.translate._translate(text_2_translate, lang)
        self.assertEqual(result, {})
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)

    @patch(
        "modules.funtranslations.FunTranslationsAPIWrapper"
        "._send_fun_translator_get"
    )
    def test_translate_bad_api_response(self, mock_send_get):
        """
        Tests translating returns the correct response when the API fails
        """
        text_2_translate = "hello, world"
        lang = TranslationLanguage.YODA
        send_translate_response = {
            "message": "Error: Too Many Requests: Rate limit of 5 requests per"
            " hour exceeded. Please wait for 59 minutes and 59 seconds"
        }
        mock_send_get.return_value = send_translate_response, 429
        result, status = self.translate._translate(text_2_translate, lang)
        self.assertEqual(result, send_translate_response)
        self.assertEqual(status, 429)

    @patch(
        "modules.funtranslations.FunTranslationsAPIWrapper"
        "._send_fun_translator_get"
    )
    def test_translate_invalid_data(self, mock_send_get):
        """
        Tests translating returns the correct response when the API data
        is not as expected
        """
        text_2_translate = "hello, world"
        lang = TranslationLanguage.YODA
        send_translate_response = {"I am a bad": "response"}
        mock_send_get.return_value = send_translate_response, 200
        result, status = self.translate._translate(text_2_translate, lang)
        self.assertEqual(result["message"], "Error: Failed to parse data")
        self.assertEqual(status, 500)

    @patch(
        "modules.funtranslations.FunTranslationsAPIWrapper"
        "._send_fun_translator_get"
    )
    def test_translate_good(self, mock_send_get):
        """
        Tests translating returns a good response
        """
        text_2_translate = "hello, world"
        lang = TranslationLanguage.YODA
        mock_send_get.return_value = mock_data.ft_translate_hello_world, 200
        result, status = self.translate._translate(text_2_translate, lang)
        expected_trans = mock_data.ft_translate_hello_world["contents"][
            "translated"
        ]
        self.assertEqual(result["translation"], expected_trans)
        self.assertEqual(status, 200)

    @patch(
        "modules.funtranslations.FunTranslationsAPIWrapper"
        "._send_fun_translator_get"
    )
    def test_translate_yoda(self, mock_send_get):
        """
        Tests the translate yoda function behaves as expected
        """
        text_2_translate = "hello, world"
        mock_send_get.return_value = mock_data.ft_translate_hello_world, 200
        self.translate.translate_yoda(text_2_translate)
        mock_send_get.assert_called_with(
            "/yoda.json", {"text": text_2_translate}
        )

    @patch(
        "modules.funtranslations.FunTranslationsAPIWrapper"
        "._send_fun_translator_get"
    )
    def test_translate_shakespeare(self, mock_send_get):
        """
        Tests the translate shakespeare function behaves as expected
        """
        text_2_translate = "hello, world"
        mock_send_get.return_value = mock_data.ft_translate_hello_world, 200
        self.translate.translate_shakespeare(text_2_translate)
        mock_send_get.assert_called_with(
            "/shakespeare.json", {"text": text_2_translate}
        )
