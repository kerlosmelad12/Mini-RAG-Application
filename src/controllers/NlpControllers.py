from .BaseControllers import BaseControllers
from models.DB_Schemas.project import Project
from models.DB_Schemas.data import DataChunk
from stores.llm.LLMenums import CoHereEnums


class NlpControllers(BaseControllers):

    def __init__(self,vectordb_client,embedding_client,generation_client):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.embedding_client=embedding_client
        self.generation_client=generation_client

    def create_collection_name (self,project_id):

        return f"collection_ {project_id}".strip()

    def reset_vector_db(self,project:Project):
        collection_name=self.create_collection_name(project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_collection_info(self,project:Project):
        collection_name=self.create_collection_name(project.project_id)
        collection_info=self.vectordb_client.get_collection_info(collection_name=collection_name)
        return collection_info

    def index_into_vector_db(self, project: Project, data_chuncks: list[DataChunk],
                          chunk_ids: list[int], do_reset: bool = False):
        collection_name = self.create_collection_name(project.id)

        texts = [c.chunk_text for c in data_chuncks]
        metadata = [c.chunk_metadata for c in data_chuncks]

        vectors = self.embedding_client.embedd_text(text=texts, document_type=CoHereEnums.DOCUMENT.value)

        

        is_created = self.vectordb_client.create_collection(
            collection_name=collection_name,
            vector_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )
        if not is_created and not self.vectordb_client.is_collection_exist(collection_name):
            return False

        is_inserted = self.vectordb_client.insert_many(
            collection_name=collection_name,
            metadata=metadata,
            texts=texts,
            vectors=vectors,
            record_ids=chunk_ids
        )

        return is_inserted