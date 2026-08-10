from .BaseControllers import BaseControllers
from models.DB_Schemas.project import Project
from models.DB_Schemas.data import DataChunk
from stores.llm.LLMenums import CoHereEnums
import  logging
import json
from stores.llm.LLMenums import GrokEnums


class NlpControllers(BaseControllers):

    def __init__(self,vectordb_client,embedding_client,generation_client,templete_client):
        super().__init__()
        self.vectordb_client=vectordb_client
        self.embedding_client=embedding_client
        self.generation_client=generation_client
        self.templete_client=templete_client
        self.logger=logging.getLogger(__name__)

    def create_collection_name(self, project_id: str) -> str:
        return f"collection_{str(project_id).strip()}"

    def reset_vector_db(self,project:Project):
        collection_name=self.create_collection_name(project.id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_collection_info(self,project:Project):
        collection_name=self.create_collection_name(project.id)
        collection_info=self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )

    def index_into_vector_db(self, project: Project, data_chuncks: list[DataChunk],
                          chunk_ids: list[int], do_reset: bool = False):
        collection_name = self.create_collection_name(project.id)

        texts = [c.chunk_text for c in data_chuncks]
        metadata = [c.chunk_metadata for c in data_chuncks]

        vectors = self.embedding_client.embedd_text(text=texts, document_type=CoHereEnums.DOCUMENT.value)

        if not vectors:
            self.logger.error("Failed to generate embeddings, aborting insert")
            return False 

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

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.id)

        # step2: get text embedding vector
        vector = self.embedding_client.embedd_text(text=text, 
                                                 )

        if not vector or len(vector) == 0:
            return False

        # step3: do semantic search
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False

        return results

    def answer_rag_question(self, project: Project, text: str, limit: int = 10):
        results = self.search_vector_db_collection(project=project, text=text, limit=limit)

        if not results or len(results) == 0:
            return None

        system_promt = self.templete_client.get("rag", "system_prompt")

        document_promts = "\n".join([
            self.templete_client.get(
                "rag",
                "user_prompt",
                {
                    "document_number": idx + 1,
                    "context": self.generation_client.process_text(doc.text),
                }
            )
            for idx, doc in enumerate(results)
        ])

        foter_promot = self.templete_client.get(
            "rag",
            "foter_prompt",
            {"question": text}          
        )

        promot = "\n\n".join([document_promts, foter_promot])

        chat_history = [self.generation_client.construct_promot(
            message=system_promt,
            role=self.generation_client.enums.SYSTEM.value)]

        answer = self.generation_client.generate_text(prompt=promot, chat_history=chat_history)

        return answer, promot, chat_history