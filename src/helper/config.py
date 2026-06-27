from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str


    FILE_TYPE_EXTENTIONS: list
    FILE_MAX_SIZE: int
    File_Chunk_Size: int

    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings()