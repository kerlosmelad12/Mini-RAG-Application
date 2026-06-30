from fastapi import FastAPI
from routes import base, data
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
app=FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings=get_settings()
    app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client=app.mongo_conn[settings.MONGODB_DB_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()




app = FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)