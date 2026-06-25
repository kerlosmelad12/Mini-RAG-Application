from fastapi import APIRouter
import os
base_router = APIRouter(
    prefix="/MiniRAG-V1",
    tags=['api_v1']
)

@base_router.get("/")
async def welcome():
    app_name=os.getenv('APP_NAME')
    version=os.getenv('APP_VERSION')
    return {"app_name": app_name,
            "app_version":version}