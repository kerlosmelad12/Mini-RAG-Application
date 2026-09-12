from celery_app import celery_app, get_setup_utils
from helper.config import get_settings
import asyncio
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.DB_Schemas import DataChunk
from models.enums.ResponseValues import ResponseValues
from controllers.ProcessControllers import ProcessControllers
from controllers.NlpControllers import NlpControllers
import logging
from utils.idempotency_manager import IdempotencyManager


logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="tasks.file_processing.process_project_files",
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_project_files(self,project_id,file_id,do_reset,overlap_size,chunk_size,file_type):

    return asyncio.run(
        _process_project_files(self,project_id,file_id,
                                       do_reset,overlap_size,chunk_size,file_type)
                                       )
    


async def _process_project_files(task_instance,project_id,file_id,
                           do_reset,overlap_size,chunk_size,file_type):

    db_engine, vectordb_client = None, None
    try:
        (db_engine,db_client,generation_client,sound,translator,embedding_client,vectordb_client,templete_parser,
                translate_factory,sound_factory,Vector_db_factory,llm_provider_factory) = await get_setup_utils()


        idempotency_manager = IdempotencyManager(db_client, db_engine)

        # Define task arguments for idempotency check
        task_args = {
            "project_id": project_id,
            "file_id": file_id,
            "chunk_size": chunk_size,
            "overlap_size": overlap_size,
            "do_reset": do_reset,
            "file_type":file_type
        }
        
        task_name = "tasks.file_processing.process_project_files"

        settings = get_settings()

        should_execute, existing_task = await idempotency_manager.should_execute_task(
            task_name=task_name,
            task_args=task_args,
            celery_task_id=task_instance.request.id,
            task_time_limit=settings.CELERY_TASK_TIME_LIMIT
        )


        if not should_execute:

            logger.warning(f"Can not handle th task | status: {existing_task.status}")
            return existing_task.result
        

        task_record = None
        if existing_task:
            # Update existing task with new celery task ID
            await idempotency_manager.update_task_status(
                execution_id=existing_task.execution_id,
                status='PENDING'
            )
            task_record = existing_task
        else:
            # Create new task record
            task_record = await idempotency_manager.create_task_record(
                task_name=task_name,
                task_args=task_args,
                celery_task_id=task_instance.request.id
            )
        
        # Update status to STARTED
        await idempotency_manager.update_task_status(
            execution_id=task_record.execution_id,
            status='STARTED'
        )

        

        project_model = await ProjectModel.create_instance(
            db_client=db_client
        )

        nlp_controller = NlpControllers(vectordb_client=vectordb_client,
                                embedding_client=embedding_client,
                                generation_client=generation_client,
                                templete_client=templete_parser,
                                translate_client=translator )

        project = await project_model.get_or_create_one(
            project_id=project_id
        )

        if project is None:


            await idempotency_manager.update_task_status(
                execution_id=task_record.execution_id,
                status='FAILURE',
                result={"signal": ResponseValues.PROJECT_NOT_FOUND.value,}
            )

            logging.error(f"Failed to get or create project for project_id: {project_id}")

            task_instance.update_state(
                        state="FAILURE",
                        meta={
                            "signal": ResponseValues.PROJECT_NOT_FOUND.value,
                        }
                    )

            raise Exception(f"Failed to get or create project for project_id: {project_id}")
        

        asset_model = await AssetModel.create_instance(
                db_client=db_client
            )

        project_assets_ids = {}

        if file_id:
            asset_record = await asset_model.get_asset(
                asset_project_id=project.project_id,
                asset_name=file_id
            )

            if asset_record is None:

                task_instance.update_state(
                        state="FAILURE",
                        meta={
                            "signal": ResponseValues.FILE_ID_ERROR.value,
                        }
                    )

                raise Exception(f"no_file_found_with_this_id {file_id}")


            project_assets_ids = {
                asset_record.asset_id: [asset_record.asset_name, asset_record.asset_type]
            }

        else:

            if not file_type:

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
                    asset_type=file_type,
                )

                project_assets_ids = {
                    record.asset_id: [record.asset_name, record.asset_type]
                    for record in project_assets
                }

            if len(project_assets_ids) == 0:

                task_instance.update_state(
                        state="FAILURE",
                        meta={
                            "signal": ResponseValues.NO_FILES_ERROR.value,
                        }
                    )

                await idempotency_manager.update_task_status(
                execution_id=task_record.execution_id,
                status='FAILURE',
                result={"signal": ResponseValues.NO_FILES_ERROR.value,}
            )

                raise Exception(f"not found files for {project_id}")
            

        process_controller = ProcessControllers(
            project_id=project_id,
            sound_controller=sound
        )

        no_records = 0
        no_files = 0

        chunk_model = await ChunkModel.create_instance(
                            db_client=db_client
                        )

        if do_reset == 1:
            collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
            _ = await vectordb_client.delete_collection(collection_name=collection_name)
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

                logger.error(f"No chunks for file_id: {file_id}")
                pass


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


        await idempotency_manager.update_task_status(
            execution_id=task_record.execution_id,
            status='SUCCESS',
            result={"signal": ResponseValues.PROCESSING_SUCCESS.value}
        )

        logger.warning(f"inserted_chunks: {no_records}")

        return {
                "signal": ResponseValues.PROCESSING_SUCCESS.value,
                "inserted_chunks": no_records,
                "processed_files": no_files,
                "project_id":project_id,
                "do_reset":do_reset
            }
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise

    finally:
        try:
            if db_engine:
                await db_engine.dispose()
            
            if vectordb_client:
                await vectordb_client.disconnect()
        except Exception as e:
            logger.error(f"Task failed while cleaning: {str(e)}")