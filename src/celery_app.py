from celery import Celery
from helper.config import get_settings

from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectordbFactory import VectordbFactory
from stores.templetes.templete_parser import TempleteParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from stores.sound.SoundFactory import SoundProviderFactory
from stores.translator.TranslatorFactory import TranslatorFactory

settings = get_settings()

async def get_setup_utils():
    settings = get_settings()
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    
    db_engine=create_async_engine(postgres_conn)
    db_client = sessionmaker( 
            db_engine, class_=AsyncSession, expire_on_commit=False
            )            
    
    llm_provider_factory = LLMFactory(settings)
    Vector_db_factory=VectordbFactory(settings,db_client)
    sound_factory = SoundProviderFactory(config=settings)
    translate_factory=TranslatorFactory(config=settings)
    
    
    
        #generation
    generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    generation_client.set_generation_model(model_id = settings.GENERATION_MODEL)
    
        #sound 
    sound=sound_factory.create(provider=settings.SOUND_PROVIDER)
    
        #translator
    translator=translate_factory.create(translator_type=settings.TRANSLATOR_BCKEND)
    
        # embedding client
    embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL,
                                                 embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
        #Vector_Store
    vectordb_client= Vector_db_factory.create(provider=settings.VECTOR_STORE_BACKEND)
    await vectordb_client.connect()
    
    templete_parser=TempleteParser(language=settings.PRIMARY_LANGUAGE,default_language=settings.DEFAULT_LANGUAGE)

    return(db_engine,db_client,generation_client,sound,translator,embedding_client,vectordb_client,templete_parser,
           translate_factory,sound_factory,Vector_db_factory,llm_provider_factory)

# Create Celery application instance
celery_app = Celery(
    "minirag",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.file_processing",
        "tasks.data_indexing",
        "tasks.process_workflow",
          "tasks.maintenance"
    ]
)

# Configure Celery with essential settings
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=[
        settings.CELERY_TASK_SERIALIZER
    ],

    # Task safety - Late acknowledgment prevents task loss on worker crash
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,

    # Time limits - Prevent hanging tasks
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,

    # Result backend - Store results for status tracking
    task_ignore_result=False,
    result_expires=3600,

    # Worker settings
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,

    # Connection settings for better reliability
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    worker_cancel_long_running_tasks_on_connection_loss=True,

    task_routes={
        "tasks.file_processing.process_project_files": {"queue": "file_processing"},
        "tasks.data_indexing.index_data_content": {"queue": "data_indexing"},
        "tasks.process_workflow.process_and_push_workflow": {"queue": "file_processing"},
        "tasks.maintenance.clean_celery_executions_table": {"queue": "default"},

    },
    beat_schedule={
        'cleanup-old-task-records': {
            'task': "tasks.maintenance.clean_celery_executions_table",
            'schedule': 10,
            'args': ()
        }
    },

    timezone='UTC',


)

celery_app.conf.task_default_queue = "default"