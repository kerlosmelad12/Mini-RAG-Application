from abc import ABC, abstractmethod


class TranslatorInterface(ABC):

    @abstractmethod
    def translate( self, text: str, target_lang: str):
        pass

    @abstractmethod
    def translate_many( self, texts: list, target_lang: str):
        pass