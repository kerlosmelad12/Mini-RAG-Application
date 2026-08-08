from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str


    FILE_TYPE_EXTENTIONS: list
    FILE_MAX_SIZE: int
    File_Chunk_Size: int

    MONGODB_URI:str
    MONGODB_DB_NAME:str

    
    GENERATION_BACKEND :str
    EMBEDDING_BACKEND :str

    GENERATION_MODEL:str=None
    EMBEDDING_MODEL:str=None

    COHERE_API_KEY:str=None
    GROQ_API_KEY:str=None


    EMBEDDING_MODEL_SIZE:int=None
    INPUT_DAFAULT_MAX_CHARACTERS:int=None
    GENERATION_DAFAULT_MAX_TOKENS:int=None
    GENERATION_DAFAULT_TEMPERATURE:float=None

    Distance_Metric:str=None
    DATABASE_FOLDER:str=None
    VECTOR_STORE_BACKEND:str

    DEFAULT_LANGUAGE:str="en"
    PRIMARY_LANGUAGE:str="en"

    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings()