import deepl
import logging

from ..TranslatorInterface import TranslatorInterface
from ..TranslatorEnums import TranslatorLanguadgeEnums


class DeepLProvider(TranslatorInterface):

    def __init__(self, api_key: str):
        self.client = deepl.DeepLClient(api_key)
        self.logger = logging.getLogger(__name__)

    def translate( self,text: str,target_lang: str = None,default_language: str = TranslatorLanguadgeEnums.AR.value):

        if not text or not text.strip():
            return text

        if not target_lang:
            target_lang = default_language

        try:

            result = self.client.translate_text(
                text,
                target_lang=target_lang
            )

            return result.text

        except Exception as e:

            self.logger.error(
                f"DeepL translation failed: {e}"
            )

            return text

    def translate_many( self, texts: list, target_lang: str = None, default_language: str = TranslatorLanguadgeEnums.AR.value):

        if not texts:
            return []

        if not target_lang:
            target_lang = default_language

        try:

            results = self.client.translate_text(
                texts,
                target_lang=target_lang
            )

            return [
                result.text
                for result in results
            ]

        except Exception as e:

            self.logger.error(
                f"DeepL batch translation failed: {e}"
            )

            return texts