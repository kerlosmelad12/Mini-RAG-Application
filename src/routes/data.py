from fastapi import APIRouter,UploadFile,Depends,status,Request
from helper.config import get_settings, Settings  
from controllers import DataControllers,ProjectControllers,ProcessControllers
from fastapi.responses import JSONResponse
from models.enums.ResponseValues import ResponseValues 
import aiofiles
import os
import logging
from .Schema.data import Processrequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.DB_Schemas.minirag.schemes.asset import Asset
from models.enums.DataTypeValues import DataTypeValues
from models.DB_Schemas.minirag.schemes.data import DataChunk
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers.NlpControllers import NlpControllers



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



    
from fastapi import APIRouter,UploadFile,Depends,status,Request
from helper.config import get_settings, Settings  
from controllers import DataControllers,ProjectControllers,ProcessControllers
from fastapi.responses import JSONResponse
from models.enums.ResponseValues import ResponseValues 
import aiofiles
import os
import logging
from .Schema.data import Processrequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.DB_Schemas.minirag.schemes.asset import Asset
from models.enums.DataTypeValues import DataTypeValues
from models.DB_Schemas.minirag.schemes.data import DataChunk
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers.NlpControllers import NlpControllers



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
async def process_endpoint(request: Request, project_id: int, process_request: Processrequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.chunk_overlap
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    nlp_controller = NlpControllers(vectordb_client=request.app.vectordb_client,
                             embedding_client=request.app.embedding_client,
                             generation_client=request.app.generation_client,
                             templete_client=request.app.templete_parser)

    project = await project_model.get_or_create_one(
        project_id=project_id
    )

    if project is None:
        logging.error(f"Failed to get or create project for project_id: {project_id}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseValues.PROJECT_NOT_FOUND.value}
        )

    asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
        )

    project_assets_ids = {}

    if process_request.file_id:
        asset_record = await asset_model.get_asset(
            asset_project_id=project.project_id,
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseValues.FILE_ID_ERROR.value,
                }
            )

        project_assets_ids = {
            asset_record.asset_id: [asset_record.asset_name, asset_record.asset_type]
        }

    else:

        if not process_request.file_type:

            project_assets = await asset_model.get_all_project_assets(
                asset_project_id=project.project_id,
            )

            project_assets_ids = {
                record.asset_id: [record.asset_name, record.asset_type]
                for record in project_assets
            }

        else:

            project_assets = await asset_model.get_all_project_assets(
                asset_project_id=project.project_id,
                asset_type=process_request.file_type,
            )

            project_assets_ids = {
                record.asset_id: [record.asset_name, record.asset_type]
                for record in project_assets
            }

        if len(project_assets_ids) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseValues.NO_FILES_ERROR.value,
                }
            )


    process_controller = ProcessControllers(
        project_id=project_id,
        sound_controller=request.app.sound
    )

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(
                        db_client=request.app.db_client
                    )

    if do_reset == 1:
        collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
        _ = await request.app.vectordb_client.delete_collection(collection_name=collection_name)
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.project_id
        )

    for asset_id, (file_id, asset_type) in project_assets_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id, asset_type=asset_type)

        if file_content is None:
            logging.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseValues.PROCESSING_FAILED.value
                }
            )

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.project_id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1

    return JSONResponse(
        content={
            "signal": ResponseValues.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files
        }
    )