from fastapi import APIRouter,UploadFile,Depends,status
from helper.config import get_settings, Settings  
from controllers import DataControllers,ProjectControllers,ProcessControllers
from fastapi.responses import JSONResponse
import aiofiles
import os
from models import ResponseValues
import logging
from .Schema.data import Processrequest
data_router = APIRouter(
    prefix="/MiniRAG-V1/data",
    tags=['api_v1','data']
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id:str,file:UploadFile,app_Settings:Settings=Depends(get_settings)):
    data_controllers=DataControllers()
    is_valid,result=data_controllers.validate_file(file)
    # Validate File 
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result":result
            }
        )
    #Save File Disk
    
    file_path,file_id=data_controllers.generate_filename(   
        original_filename=file.filename,
        project_id=project_id
        )
    
    try:
         async with aiofiles.open(file_path, "wb") as f:
              while chunk := await file.read(get_settings().File_Chunk_Size):
                  await f.write(chunk)


    except Exception as e:
       logging.error("The File is Faild To Save In Disk{e}")
       return JSONResponse(
           status=status.HTTP_400_BAD_REQUEST,
           content={
                "signal": ResponseValues.FILE_UPLOAD_FAILD.value,
            }    
            )
    

    return JSONResponse(
          content={
                "signal": ResponseValues.FILE_UPLOAD_SUCCSESS.value,
                'file_id':file_id
            }    
            )
    
@data_router.post("/process/{project_id}")
async def process_data(project_id:str, process_request: Processrequest):
    # Declar the procces reguest
    file_id=process_request.file_id
    chunk_size=process_request.chunk_size
    chunk_overlap=process_request.chunk_overlap

    process_controllers=ProcessControllers(project_id)


    content=process_controllers.get_file_content(file_id)
    file_chunks = process_controllers.process_file_content(
        file_content=content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=chunk_overlap
    )

    if not file_chunks and len(content)==0:
         return JSONResponse(
           status=status.HTTP_400_BAD_REQUEST,
           content={
                "signal": ResponseValues.PROCESSING_FAILED.value,
            }    
            )
    
    return file_chunks
    

   

    

    


    