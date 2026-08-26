from .TranslatorEnums import TranslatorEnums
from .providers.DeepLProvider import DeepLProvider


class TranslatorFactory:

    def __init__(self,config:object):
        self.config=config
        

    
    def create(self,translator_type: str):

        if translator_type == TranslatorEnums.DEEPL.value:
            return DeepLProvider(api_key=self.config.DEEPL_API)

        return None

      