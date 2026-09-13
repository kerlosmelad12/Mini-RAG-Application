from fastapi import APIRouter,Depends,status,Request
from .Schema.nlp import PushRequest
from models.ProjectModel import ProjectModel
from fastapi.responses import JSONResponse
from models.enums.ResponseValues import ResponseValues
from models.ChunkModel import ChunkModel
from controllers import NlpControllers
from .Schema.nlp import SearchRequest
import logging
from tqdm import tqdm
from tasks.data_indexing import index_data_content

logger= logging.getLogger("uvicorn.error")



nlp_router = APIRouter(
    prefix="/MiniRAG-V1/nlp",
    tags=['api_v1','nlp']
)

@nlp_router.post("/index/push/{project_id}")

async def index_project (project_id:int,push_request:PushRequest):

    task=index_data_content.delay(project_id=project_id,
                             do_rest=push_request.do_rest)

    return JSONResponse(
        content={
            "signal": ResponseValues.TASK_QUEUED.value,
            "task_id": task.id
        }
    )


@nlp_router.get("/index/info/{project_id}")

async def get_project_info(project_id:int,res:Request):

      
      project_model=await ProjectModel.create_instance(res.app.db_client)
      nlp_controller=NlpControllers(vectordb_client=res.app.vectordb_client,
                         embedding_client=res.app.embedding_client,
                         generation_client=res.app.generation_client,
                         templete_client=res.app.templete_parser,
                         translate_client=res.app.translator
                         )


      project=await project_model.get_project(project_id)

      if project is None:
                 return JSONResponse(
                           status_code=status.HTTP_400_BAD_REQUEST,
                           content={
                               "result":ResponseValues.NO_PROJECT_TO_EMBEDDING_DATA.value
                           }
                       )
      collection_info=await nlp_controller.get_collection_info(project)

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
async def search_index(res: Request, project_id: int, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=res.app.db_client
    )
    chunk_model=await ChunkModel.create_instance(
        db_client=res.app.db_client
    )

    project = await project_model.get_project(
        project_id=project_id
    )

    if project is None:
            return JSONResponse(
                           status_code=status.HTTP_400_BAD_REQUEST,
                           content={
                               "signal": ResponseValues.NO_PROJECT_TO_EMBEDDING_DATA.value
                           }
                       )

    book_language=await chunk_model.get_dominant_language(project_id=project.project_id)

    

    nlp_controller=NlpControllers(vectordb_client=res.app.vectordb_client,
                         embedding_client=res.app.embedding_client,
                         generation_client=res.app.generation_client,
                         templete_client=res.app.templete_parser,
                        translate_client=res.app.translator
                                                   )


    results = await nlp_controller.search_vector_db_collection(
        project=project, text=search_request.text, 
        limit=search_request.limit,
        book_language=book_language
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

@nlp_router.post("/index/answer/{project_id}")
async def answer_index(res: Request, project_id: int, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=res.app.db_client)
    chunk_model = await ChunkModel.create_instance(res.app.db_client) 
    project = await project_model.get_project(project_id=project_id)

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseValues.NO_PROJECT_TO_EMBEDDING_DATA.value}
        )

    book_language=await chunk_model.get_dominant_language(project_id=project.project_id)

    nlp_controller = NlpControllers(
        vectordb_client=res.app.vectordb_client,
        embedding_client=res.app.embedding_client,
        generation_client=res.app.generation_client,
        templete_client=res.app.templete_parser,
         translate_client=res.app.translator

    )

    answer, promot, chat_history = await nlp_controller.answer_rag_question(
        project=project, text=search_request.text,  limit=search_request.limit,book_language=book_language
    )


    if answer is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseValues.VECTORDB_SEARCH_ERROR.value}
        )

    return JSONResponse(
        content={
            "signal": ResponseValues.ANSWER_SUCSESS.value,
            "answer": answer,
            "chat_history": chat_history,
            "promot": promot
        }
    )