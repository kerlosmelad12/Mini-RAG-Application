from ..LLMInterface import LLMInterface
import logging
from ..LLMenums import GrokEnums
from groq import Groq

class GrokProvider(LLMInterface):
    def __init__(self ,api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        

        self.api_key=api_key
        self.default_input_max_characters=default_input_max_characters
        self.default_generation_max_output_tokens=default_generation_max_output_tokens
        self.default_generation_temperature=default_generation_temperature

        self.client=Groq(api_key=self.api_key)
        self.logger=logging.getLogger(__name__)

        self.generation_model_id=None


    def set_generation_model(self,model_id:str):
        self.generation_model_id=model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
      raise NotImplementedError(
        "Embedding models are not supported by Grok."
      )       

    def embedd_text(self, text: str, document_type: str = None):
      raise NotImplementedError(
        "Grok does not provide an embedding API. Use another provider such as Cohere, Gemini, or OpenAI for embeddings."
       )



    def generate_text(self,prompt: str,chat_history: list=[],
                      max_output_tokens: int = None,
                      temperature: float = None,):
        
        if not self.generation_model_id:
                self.logger.error("Grok generation model id not added")
                return None

        if not self.client:
            self.logger.error("Grok client not supported")
            return None

        temperature = temperature if temperature is not None else self.default_generation_temperature
        

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_tokens

        chat_history.append(
            self.construct_promot(self.process_text(prompt),
                                                  GrokEnums.USER.value)
                                                  )
        

        response = self.client.chat.completions.create(
            
        model=self.generation_model_id,
        messages=chat_history,
        temperature=temperature,
        max_tokens=max_output_tokens,
        )

        if not response or not response.choices or not response.choices[0] or not response.choices[0].message or not response.choices[0].message.content:
            self.logger.error("Error while generating text with Grok")
            return None

        return response.choices[0].message.content
    
    def construct_promot(self, message: str, role: str):
        return {
        "role": role,
        "content": self.process_text(message),
        }
    
     
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()