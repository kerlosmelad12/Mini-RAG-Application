from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str


    FILE_TYPE_EXTENTIONS: list
    SOUND_TYPE_EXTENSIONS:List
    FILE_MAX_SIZE: int
    SOUND_MAX_SIZE:int
    File_Chunk_Size: int

    POSTGRES_MAIN_DATABASE:str
    POSTGRES_PORT:int
    POSTGRES_HOST:str
    POSTGRES_PASSWORD:str
    POSTGRES_USERNAME:str


    
    GENERATION_BACKEND :str
    EMBEDDING_BACKEND :str

    GENERATION_MODEL:str=None
    EMBEDDING_MODEL:str=None
    EMBEDDING_MODEL_LITERAL:List
    GENERATION_MODEL_LITERAL:List

    COHERE_API_KEY:str=None
    GROQ_API_KEY:str=None


    EMBEDDING_MODEL_SIZE:int=None
    INPUT_DAFAULT_MAX_CHARACTERS:int=None
    GENERATION_DAFAULT_MAX_TOKENS:int=None
    GENERATION_DAFAULT_TEMPERATURE:float=None

    Distance_Metric:str=None
    DATABASE_PATH:str=None
    VECTOR_STORE_BACKEND:str
    VECTOR_STORE_BACKEND_LITERAL:list
    VECTOR_DB_PGVEC_INDEX_THRESHOLD:int

    DEFAULT_LANGUAGE:str="en"
    PRIMARY_LANGUAGE:str="en"

    WHISPER_LANGUAGE:str
    WHISPER_COMPUTE_TYPE:str
    WHISPER_DEVICE:str
    WHISPER_MODEL_SIZE:str
    SOUND_PROVIDER:str

    DEEPL_API:str
    TRANSLATOR_BCKEND:str
    DEAFULT_TRANSLATED_LANGUAGE:str


    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings()