import os
import requests

from http import HTTPStatus
from enum import Enum, auto


class TranslationLanguage(Enum):
    YODA = auto()
    SHAKESPEARE = auto()


class FunTranslationsAPIWrapper:
    # The URL of Funtranslations, including the inital API path
    FUNTRANSLATIONS_URL = os.environ.get("FUNTRANSLATIONS_URL", None)
    # Set the maximum timeout time of every request
    REQUEST_TIMEOUT_TIME = 10

    def __init__(self):
        """
        Initialise the wrapper
        """
        if FunTranslationsAPIWrapper.FUNTRANSLATIONS_URL is None:
            raise RuntimeError(
                "Missing required environment variable "
                "'FunTranslationsAPIWrapper'"
            )

    def _build_fun_translator_url(self, path):
        """
        Given a path, builds the funtranslations.com URL
        :param path: String API path to target
        :return: String full URL to target
        """
        if path.startswith("/"):
            return f"{FunTranslationsAPIWrapper.FUNTRANSLATIONS_URL}{path}"
        return f"{FunTranslationsAPIWrapper.FUNTRANSLATIONS_URL}/{path}"

    def _send_fun_translator_get(self, path, params={}):
        """
        A generic method to send GET requests to funtranslations.com
        :param path: String target path to hit on the API
        :param params: Dict of GET parameters to send with the request
        :return: A Tuple containing:
        - Dict of the response data
        - Integer HTTP Status Code
        """
        result = {}
        url = self._build_fun_translator_url(path)
        try:
            response = requests.get(
                url,
                params=params,
                timeout=FunTranslationsAPIWrapper.REQUEST_TIMEOUT_TIME,
            )
            json_data = response.json()
            if response.status_code != HTTPStatus.OK:
                error = json_data["error"]["message"]
                result["message"] = f"Error: {error}"
                return result, response.status_code
            return json_data, response.status_code
        except requests.exceptions.RequestException:
            result[
                "message"
            ] = "Error: Failed to retrieve data, please try again later"
        except Exception:
            result[
                "message"
            ] = "Error: Bad response received from remote server"
        return result, HTTPStatus.INTERNAL_SERVER_ERROR

    def _translate(self, text_to_translate, translation_lang):
        """
        Translates a string to a given translation language
        :param text_to_translate: String text to translate to Shakespeare
        :param translation_lang: TranslationLanguage to use
        """
        params = {"text": text_to_translate}
        if translation_lang == TranslationLanguage.YODA:
            endpoint = "/yoda.json"
        elif translation_lang == TranslationLanguage.SHAKESPEARE:
            endpoint = "/shakespeare.json"
        else:
            return {}, HTTPStatus.BAD_REQUEST

        result, status_code = self._send_fun_translator_get(endpoint, params)
        if status_code != HTTPStatus.OK:
            return result, status_code

        try:
            translated_text = result["contents"]["translated"]
        except Exception:
            return {
                "message": "Error: Failed to parse data"
            }, HTTPStatus.INTERNAL_SERVER_ERROR
        return {"translation": translated_text}, HTTPStatus.OK

    def translate_yoda(self, text_to_translate):
        """
        Given a string, translates it to the Yoda equivalent
        :param text_to_translate: String text to translate to Yoda
        :return: A Tuple containing:
        - Dict of the response data
        - Integer HTTP Status Code
        """
        return self._translate(text_to_translate, TranslationLanguage.YODA)

    def translate_shakespeare(self, text_to_translate):
        """
        Given a string, translates it to the Shakespeare equivalent
        :param text_to_translate: String text to translate to Shakespeare
        :return: A Tuple containing:
        - Dict of the response data
        - Integer HTTP Status Code
        """
        return self._translate(
            text_to_translate, TranslationLanguage.SHAKESPEARE
        )
