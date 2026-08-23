from fastapi import FastAPI
from routes import base, data, nlp
import uvicorn
from helper.config import get_settings
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectordbFactory import VectordbFactory
from stores.templetes.templete_parser import TempleteParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from stores.sound.SoundFactory import SoundProviderFactory


app = FastAPI()

@app.on_event("startup")

async def startup_span():
    settings = get_settings()
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine=create_async_engine(postgres_conn)
    app.db_client = sessionmaker( 
        app.db_engine, class_=AsyncSession, expire_on_commit=False
)

    llm_provider_factory = LLMFactory(settings)
    Vector_db_factory=VectordbFactory(settings,app.db_client)
    sound_factory = SoundProviderFactory(config=settings)



    #generation
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL)

    #sound 
    app.sound=sound_factory.create(provider=settings.SOUND_PROVIDER)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

    #Vector_Store
    app.vectordb_client= Vector_db_factory.create(provider=settings.VECTOR_STORE_BACKEND)
    await app.vectordb_client.connect()

    app.templete_parser=TempleteParser(language=settings.PRIMARY_LANGUAGE,default_language=settings.DEFAULT_LANGUAGE)

   
    

@app.on_event("shutdown")

async def shutdown_span():
    app.db_engine.dispose()
    



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)