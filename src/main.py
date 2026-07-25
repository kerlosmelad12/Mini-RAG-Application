from fastapi import FastAPI
from routes import base, data, nlp
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectordbFactory import VectordbFactory

app = FastAPI()

@app.on_event("startup")

async def startup_span():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client = app.mongo_conn[settings.MONGODB_DB_NAME]
    llm_provider_factory = LLMFactory(settings)
    Vector_db_factory=VectordbFactory(settings)
    #generation
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

    #Vector_Store
    app.qdrant= Vector_db_factory.create(provider=settings.VECTOR_STORE_BACKEND)
    app.qdrant.set_distance_metric(settings.Distance_Metric)
    app.qdrant.connect()

@app.on_event("shutdown")

async def shutdown_span():
    app.mongo_conn.close()
    app.qdrant.disconnect()



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)