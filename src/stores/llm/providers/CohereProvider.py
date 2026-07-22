from ..LLMInterface import LLMInterface
import cohere
import logging
from ..LLMenums import CoHereEnums
class CohereProvider(LLMInterface):
    def __init__(self ,api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        

        self.api_key=api_key
        self.default_input_max_characters=default_input_max_characters
        self.default_generation_max_output_tokens=default_generation_max_output_tokens
        self.default_generation_temperature=default_generation_temperature

        self.client=cohere.Client(api_key=self.api_key)
        self.logger=logging.getLogger(__name__)


        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None

    def set_generation_model(self,model_id:str):
        self.generation_model_id=model_id

    def set_embedding_model(self,model_id:str,embedding_size:int):
        self.embedding_model_id= model_id
        self.embedding_size=embedding_size


    def embedd_text(self,text:str,document_type:str=None):

        if not self.embedding_model_id:
            self.logger.error("cohere embedding model id not added")
            return None


        if not self.client:
            self.logger.error("cohere client not supported")
            return None
        
        input_type=CoHereEnums.DOCUMENT.value

        if document_type!=input_type:
            input_type=CoHereEnums.QUERY.value

        response=self.client.embed(
            texts=[self.process_text(text)],
            model=self.embedding_model_id,
            input_type=input_type,
            output_dimension=self.embedding_size,
            embedding_types=['float']

        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        
        return response.embeddings.float[0]
    

    
    def generate_text(self,prompt:str,chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        
        if not self.generation_model_id:
             self.logger.error("cohere generation model id not added")

        
        if not self.client:
            self.logger.error("cohere client not supported")
            return None
        
        temperature=temperature if temperature else self.default_generation_temperature
        max_output_tokens=max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens

        response = self.client.chat(

            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None
        
        return response.text
    
    
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()
    

    def construct_promot(self,message:str,role:str):

        return{

            "role":role,
            "content":self.process_text(message)
        }
        


        


