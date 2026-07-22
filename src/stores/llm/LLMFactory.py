from .providers.GrokProvider import GrokProvider
from .providers.CohereProvider import CohereProvider
from .LLMenums import LLMEnums

class LLMFactory:
    def __init__(self,config:dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.GROK.value:
            return GrokProvider(
                api_key=self.config.GROK_API_KEY,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE,
            )

        elif provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE,
            )

        return None