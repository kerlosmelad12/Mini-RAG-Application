from .providers import PGVectorProvider,QDrantProvider
from .VectordbEnums import VectordbEnums
from controllers.BaseControllers import BaseControllers
from sqlalchemy.orm import sessionmaker



class VectordbFactory:
    def __init__(self,config,db_client: sessionmaker=None):
        self.base_controller=BaseControllers()
        self.config=config
        self.db_client=db_client

    def create(self,provider:str):

        if provider==VectordbEnums.QDRANT.value:
            qdrant_db_client = self.base_controller.get_database_path(db_name=self.config.DATABASE_PATH)

            return QDrantProvider(
                        db_client=qdrant_db_client,
                        distance_method=self.config.Distance_Metric,
                        default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                        index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD,
                    )
        
        elif provider == VectordbEnums.PGVECTOR.value:
                return PGVectorProvider(
                        db_client=self.db_client,
                        distance_method=self.config.Distance_Metric,
                        default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                        index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD,
                    )
                



        
            
        
