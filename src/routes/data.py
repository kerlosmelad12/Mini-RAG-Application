from fastapi import APIRouter,UploadFile,Depends,status,Request
from helper.config import get_settings, Settings  
from controllers import DataControllers
from fastapi.responses import JSONResponse
from models.enums.ResponseValues import ResponseValues 
import aiofiles
import os
import logging
from .Schema.data import Processrequest
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.DB_Schemas.minirag.schemes.asset import Asset
from models.enums.DataTypeValues import DataTypeValues
from tasks.file_processing import process_project_files
from tasks.process_workflow import process_and_push_workflow
from celery.result import AsyncResult
from celery_app import celery_app
from utils.idempotency_manager import IdempotencyManager
from helper.config import get_settings
from fastapi import Request
from fastapi.responses import JSONResponse
from models.enums.ResponseValues import ResponseValues


data_router = APIRouter(
    prefix="/MiniRAG-V1/data",
    tags=['api_v1','data']
)

@data_router.post("/upload/file/{project_id}")
async def upload_file(request:Request,project_id:int,file:UploadFile,app_Settings:Settings=Depends(get_settings)):

    project_model=await ProjectModel.create_instance(request.app.db_client)

    project=await project_model.get_or_create_one(project_id)

    data_controllers=DataControllers()

    is_valid,requestult=data_controllers.validate_file(file)


    # Validate File 
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "requestult":requestult
            }
        )
    
    #Save File Disk
    
    file_path,file_id=data_controllers.generate_filename(   
        original_filename=file.filename,
        project_id=project_id,
        file_type=DataTypeValues.FILE.value

        )
    
    try:
         async with aiofiles.open(file_path, "wb") as f:
              while chunk := await file.read(get_settings().File_Chunk_Size):
                  await f.write(chunk)


    except Exception as e:
       logging.error("The File is Faild To Save In Disk{e}")
       return JSONResponse(
           status_code=status.HTTP_400_BAD_REQUEST,
           content={
                "signal": ResponseValues.FILE_UPLOAD_FAILD.value,
            }    
            )
    

    asset_model=await AssetModel.create_instance(db_client=request.app.db_client)

    asset=Asset(
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_type=DataTypeValues.FILE.value,
        asset_project_id=project.project_id)
    asset_record=await asset_model.insert_asset(asset)



    return JSONResponse(
          content={
                "signal": ResponseValues.FILE_UPLOAD_SUCCSESS.value,
                'file_id':str(asset_record.asset_id),
            }    
            )


@data_router.post("/upload/audio/{project_id}")
async def upload_audio(request:Request,project_id:int,file:UploadFile,app_Settings:Settings=Depends(get_settings)):

    project_model=await ProjectModel.create_instance(request.app.db_client)

    project=await project_model.get_or_create_one(project_id)

    data_controllers=DataControllers()

    is_valid,requestult=data_controllers.validate_sound(file)


    # Validate File 
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "requestult":requestult
            }
        )
    
    #Save File Disk
    
    file_path,file_id=data_controllers.generate_filename(   
        original_filename=file.filename,
        project_id=project_id,
        file_type=DataTypeValues.SOUND.value
        )
    
    try:
         async with aiofiles.open(file_path, "wb") as f:
              while chunk := await file.read(get_settings().File_Chunk_Size):
                  await f.write(chunk)


    except Exception as e:
       logging.error("The File is Faild To Save In Disk{e}")
       return JSONResponse(
           status_code=status.HTTP_400_BAD_REQUEST,
           content={
                "signal": ResponseValues.FILE_UPLOAD_FAILD.value,
            }    
            )

    asset_model=await AssetModel.create_instance(db_client=request.app.db_client)

    asset=Asset(
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        asset_type=DataTypeValues.SOUND.value,
        asset_project_id=project.project_id)
    asset_record=await asset_model.insert_asset(asset)



    return JSONResponse(
          content={
                "signal": ResponseValues.FILE_UPLOAD_SUCCSESS.value,
                'file_id':str(asset_record.asset_id),
            }    
            ) 



@data_router.post("/process/{project_id}")
async def process_endpoint( project_id: int, process_request: Processrequest):

    task = process_project_files.delay(
        project_id=project_id, file_id=process_request.file_id,
        do_reset=process_request.do_reset, overlap_size=process_request.chunk_overlap,
        chunk_size=process_request.chunk_size, file_type=process_request.file_type
    )

    return JSONResponse(
        content={
            "signal": ResponseValues.TASK_QUEUED.value,  
            "task_id": task.id
        }
    )


@data_router.post("/process-push/{project_id}")
async def process_and_push_endpoint(project_id: int, process_request: Processrequest):

    workflow_task = process_and_push_workflow.delay(
        project_id=project_id, file_id=process_request.file_id,
        do_reset=process_request.do_reset, overlap_size=process_request.chunk_overlap,
        chunk_size=process_request.chunk_size, file_type=process_request.file_type
    )

    return JSONResponse(
        content={
            "signal": ResponseValues.TASK_QUEUED.value,  
            "workflow_task_id": workflow_task.id
        }
    )

