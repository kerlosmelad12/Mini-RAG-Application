from fastapi import APIRouter,UploadFile,Depends,status
from helper.config import get_settings, Settings  
from controllers import DataControllers
from fastapi.responses import JSONResponse
data_router = APIRouter(
    prefix="/MiniRAG-V1/data",
    tags=['api_v1','data']
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id:str,file:UploadFile,app_Settings:Settings=Depends(get_settings)):
    is_valid,result=DataControllers().validate_file(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result":result
            }
        )


    