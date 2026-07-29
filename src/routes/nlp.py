from fastapi import APIRouter,Depends,status,Request
from helper.config import get_settings, Settings  
from .Schema.nlp import PushRequest
from models.ProjectModel import ProjectModel
from fastapi.responses import JSONResponse
from models.enums.ResponseValues import ResponseValues
from models.ChunkModel import ChunkModel
from controllers import NlpControllers
from .Schema.nlp import SearchRequest
import logging
logger= logging.getLogger("uvicorn.error")



nlp_router = APIRouter(
    prefix="/MiniRAG-V1/nlp",
    tags=['api_v1','nlp']
)

@nlp_router.post("/index/push/{project_id}")

async def index_project (project_id:str,res:Request,push_request:PushRequest):

    
    project_model=await ProjectModel.create_instance(res.app.db_client)
    chunk_model=await ChunkModel.create_instance(res.app.db_client)

    
    project=await project_model.get_project(project_id)

    if project is None:
           return JSONResponse(
                     status_code=status.HTTP_400_BAD_REQUEST,
                     content={
                         "result":ResponseValues.NO_PROJECT_TO_EMBEDDING_DATA.value
                     }
                 )

    
    nlp_controller=NlpControllers(vectordb_client=res.app.qdrant,
                   embedding_client=res.app.embedding_client,
                   generation_client=res.app.generation_client)
    
    has_records=True
    page_no=1
    inserted_items_count=0
    index=0
    first_page=True

    while has_records:
        page_chunks=await chunk_model.get_chunks_by_projectid(project_id=str(project.id), page_no=page_no)

        if not page_chunks or len(page_chunks)==0:
            has_records=False
            break

        page_no+=1
        chunk_ids=list(range(index, index+len(page_chunks)))
        index+=len(page_chunks)

        is_insterted=nlp_controller.index_into_vector_db(
            project=project,
            data_chuncks=page_chunks,
            do_reset=push_request.do_rest if first_page else False,   # only reset on first page
            chunk_ids=chunk_ids
        )
        first_page=False

        if not is_insterted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"result": ResponseValues.NO_DATA_ISTERSTEDIN_VECTOR.value}
            )
        inserted_items_count += len(page_chunks)

    return JSONResponse(
                         content={
                             "result":ResponseValues.INSERTED_SCUSSCFULLY_VECTORDB.value
                         }
                     )
@nlp_router.get("/index/info/{project_id}")

async def get_project_info(project_id:str,res:Request):

      
      project_model=await ProjectModel.create_instance(res.app.db_client)
      nlp_controller=NlpControllers(vectordb_client=res.app.qdrant,
                         embedding_client=res.app.embedding_client,
                         generation_client=res.app.generation_client)


      project=await project_model.get_project(project_id)

      if project is None:
                 return JSONResponse(
                           status_code=status.HTTP_400_BAD_REQUEST,
                           content={
                               "result":ResponseValues.NO_PROJECT_TO_EMBEDDING_DATA.value
                           }
                       )
      collection_info=nlp_controller.get_collection_info(project)

      if collection_info is None:
                       return JSONResponse(
                                 status_code=status.HTTP_400_BAD_REQUEST,
                                 content={
                                     "result":ResponseValues.COLLECTION_INFO_FAILD.value
                                 }
                             ) 
      return JSONResponse(
                            content={
                                   "collection_info":collection_info,
                                    "result":ResponseValues.COLLECTION_INFO_SUCCSESS.value
                                        }
                                   ) 

@nlp_router.post("/index/search/{project_id}")
async def search_index(res: Request, project_id: str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=res.app.db_client
    )

    project = await project_model.get_project(
        project_id=project_id
    )

    nlp_controller=NlpControllers(vectordb_client=res.app.qdrant,
                         embedding_client=res.app.embedding_client,
                         generation_client=res.app.generation_client)

    results = nlp_controller.search_vector_db_collection(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseValues.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": ResponseValues.VECTORDB_SEARCH_SUCCESS.value,
            "results": [ result.dict()  for result in results ]
        }
    )

      
      

     

    
              
              
    
              
