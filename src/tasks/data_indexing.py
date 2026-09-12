from celery_app import celery_app, get_setup_utils
from helper.config import get_settings
import asyncio
import logging
from models.enums.ResponseValues import ResponseValues
from models.ChunkModel import ChunkModel
from controllers import NlpControllers
from models.ProjectModel import ProjectModel
from tqdm import tqdm
from utils.idempotency_manager import IdempotencyManager

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.data_indexing.index_data_content",
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60})
def index_data_content(self, do_rest, project_id):

    return asyncio.run(
        _index_data_content(self, do_rest=do_rest, project_id=project_id))


async def _index_data_content(task_instance, do_rest, project_id):

    db_engine, vectordb_client = None, None

    try:

        (db_engine, db_client, generation_client, sound, translator, embedding_client, vectordb_client, templete_parser,
         translate_factory, sound_factory, Vector_db_factory, llm_provider_factory) = await get_setup_utils()

        idempotency_manager = IdempotencyManager(db_client, db_engine)

        task_args = {
            "project_id": project_id,
            "do_rest": do_rest,
        }

        task_name = "tasks.data_indexing.index_data_content"

        settings = get_settings()

        should_execute, existing_task = await idempotency_manager.should_execute_task(
            task_name=task_name,
            task_args=task_args,
            celery_task_id=task_instance.request.id,
            task_time_limit=settings.CELERY_TASK_TIME_LIMIT
        )

        if not should_execute:
            logger.warning(f"Can not handle the task | status: {existing_task.status}")
            return existing_task.result

        task_record = None
        if existing_task:
            await idempotency_manager.update_task_status(
                execution_id=existing_task.execution_id,
                status='PENDING'
            )
            task_record = existing_task
        else:
            task_record = await idempotency_manager.create_task_record(
                task_name=task_name,
                task_args=task_args,
                celery_task_id=task_instance.request.id
            )

        await idempotency_manager.update_task_status(
            execution_id=task_record.execution_id,
            status='STARTED'
        )

        project_model = await ProjectModel.create_instance(db_client)
        chunk_model = await ChunkModel.create_instance(db_client)

        project = await project_model.get_project(project_id)

        if project is None:

            logging.error(f"Failed to get or create project for project_id: {project_id}")

            await idempotency_manager.update_task_status(
                execution_id=task_record.execution_id,
                status='FAILURE',
                result={"signal": ResponseValues.NO_PROJECT_TO_EMBEDDING_DATA.value}
            )

            task_instance.update_state(
                state="FAILURE",
                meta={
                    "signal": ResponseValues.NO_PROJECT_TO_EMBEDDING_DATA.value,
                })
            raise Exception(f"Failed to get or create project for project_id: {project_id}")

        nlp_controller = NlpControllers(vectordb_client=vectordb_client,
                                         embedding_client=embedding_client,
                                         generation_client=generation_client,
                                         templete_client=templete_parser,
                                         translate_client=translator)

        has_records = True
        page_no = 1
        inserted_items_count = 0
        index = 0
        first_page = True

        # create collection if not exists
        collection_name = nlp_controller.create_collection_name(project_id=project.project_id)

        _ = await vectordb_client.create_collection(
            collection_name=collection_name,
            vector_size=embedding_client.embedding_size,
            do_reset=do_rest,
        )

        # setup batching
        total_chunks_count = await chunk_model.get_total_chunks_count(project_id=project.project_id)
        pbar = tqdm(total=total_chunks_count, desc="Vector Indexing", position=0)

        while has_records:
            page_chunks = await chunk_model.get_chunks_by_projectid(project_id=project.project_id, page_no=page_no)

            if not page_chunks or len(page_chunks) == 0:
                has_records = False
                break

            page_no += 1
            chunk_ids = [c.chunk_id for c in page_chunks]
            index += len(page_chunks)

            is_insterted = await nlp_controller.index_into_vector_db(
                project=project,
                data_chuncks=page_chunks,
                chunk_ids=chunk_ids
            )

            if not is_insterted:
                logger.error("no inserted data in vectordb")

                await idempotency_manager.update_task_status(
                    execution_id=task_record.execution_id,
                    status='FAILURE',
                    result={"signal": ResponseValues.NO_DATA_ISTERSTEDIN_VECTOR.value}
                )

                task_instance.update_state(
                    state="FAILURE",
                    meta={
                        "signal": ResponseValues.NO_DATA_ISTERSTEDIN_VECTOR.value,
                    }
                )

                raise Exception(f"no inserted data in vectordb for {project_id}")

            pbar.update(len(page_chunks))
            inserted_items_count += len(page_chunks)

        logger.info(f"insertred count {inserted_items_count}")

        result = {
            "result": ResponseValues.INSERTED_SCUSSCFULLY_VECTORDB.value,
            "inserted count": inserted_items_count
        }

        await idempotency_manager.update_task_status(
            execution_id=task_record.execution_id,
            status='SUCCESS',
            result=result
        )

        return result

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