import logging
import json
import asyncio
from typing import Optional, Tuple, Any
from .BaseControllers import BaseControllers
from models.DB_Schemas.minirag.schemes.project import Project
from models.DB_Schemas.minirag.schemes.data import DataChunk
from stores.llm.LLMenums import CoHereEnums
from models.enums.AssetTypeEnum import Assetlanguadge


class NlpControllers(BaseControllers):

    def __init__(self, vectordb_client, embedding_client, generation_client, templete_client, translate_client):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_client = templete_client
        self.translate_client = translate_client
        self.logger = logging.getLogger(__name__)

    def create_collection_name(self, project_id: str) -> str:
        return f"collection_{self.vectordb_client.default_vector_size}_{str(project_id).strip()}"

    async def reset_vector_db(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)

    async def get_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)
        
        # Safe dict conversion
        if hasattr(collection_info, "dict"):
            return collection_info.dict()
        return json.loads(json.dumps(collection_info, default=lambda x: getattr(x, "__dict__", str(x))))

    async def index_into_vector_db(self, project: Project, data_chuncks: list[DataChunk],
                                    chunk_ids: list[int], do_reset: bool = False) -> bool:
        collection_name = self.create_collection_name(project.project_id)

        texts = [c.chunk_text for c in data_chuncks]
        metadata = [c.chunk_metadata for c in data_chuncks]

        # Offload sync embedding calls to prevent loop blocking
        vectors = await asyncio.to_thread(
            self.embedding_client.embedd_text,
            text=texts,
            document_type=CoHereEnums.DOCUMENT.value
        )

        if not vectors:
            self.logger.error("Failed to generate embeddings, aborting insert")
            return False

        is_created = await self.vectordb_client.create_collection(
            collection_name=collection_name,
            vector_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )
        if not is_created and not await self.vectordb_client.is_collection_exist(collection_name):
            return False

        return await self.vectordb_client.insert_many(
            collection_name=collection_name,
            metadata=metadata,
            texts=texts,
            vectors=vectors,
            record_ids=chunk_ids
        )

    async def search_vector_db_collection(self, project: Project, text: str,
                                           book_language: str, limit: int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        query_text = self.clean_text(text)

        # Language translation if necessary
        if self.detect_language(query_text) != book_language:
            deepl_target = Assetlanguadge(book_language).to_deepl_code()
            query_text = await asyncio.to_thread(
                self.translate_client.translate,
                text=query_text,
                target_lang=deepl_target
            )
            query_text = self.clean_text(query_text)

        # Embedding query vector asynchronously
        vector = await asyncio.to_thread(self.embedding_client.embedd_text, text=query_text)

        if not vector:
            return False

        return await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

    async def answer_rag_question(self, project: Project, text: str, book_language: str, limit: int = 10) -> Optional[Tuple[Any, str, list]]:
        results = await self.search_vector_db_collection(
            project=project, text=text, book_language=book_language, limit=limit
        )

        if not results:
            return None

        system_prompt = self.template_client.get("rag", "system_prompt")

        document_prompts = "\n".join([
            self.template_client.get(
                "rag", "user_prompt",
                {
                    "document_number": idx + 1,
                    "context": self.generation_client.process_text(doc.text),
                }
            )
            for idx, doc in enumerate(results)
        ])

        footer_prompt = self.template_client.get("rag", "foter_prompt", {"question": text})
        full_prompt = "\n\n".join([document_prompts, footer_prompt])

        chat_history = [
            self.generation_client.construct_promot(
                message=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        answer = await asyncio.to_thread(
            self.generation_client.generate_text,
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history