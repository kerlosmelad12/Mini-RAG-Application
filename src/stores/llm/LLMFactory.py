from .providers.GrokProvider import GrokProvider
from .providers.CohereProvider import CohereProvider
from .providers.MiniLmProvider import LocalEmbeddingProvider
from .LLMenums import LLMEnums

class LLMFactory:
    def __init__(self,config:dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.GROQ.value:
            return GrokProvider(
                api_key=self.config.GROQ_API_KEY,
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
        elif provider == LLMEnums.LOCALLLM.value:
            return LocalEmbeddingProvider(
                model_name=self.config.EMBEDDING_MODEL,
                input_defualt_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS
            )

        return None