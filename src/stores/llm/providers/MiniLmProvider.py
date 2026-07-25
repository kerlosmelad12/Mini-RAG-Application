import logging
from sentence_transformers import SentenceTransformer
from stores.llm.LLMInterface import LLMInterface  # adjust import path to match your project structure


class LocalEmbeddingProvider(LLMInterface):


    def __init__(self, model_name: str = "all-MiniLM-L6-v2", embedding_size: int = 384):
        self.logger = logging.getLogger(__name__)

        self.generation_model_id = None
        self.embedding_model_id = model_name
        self.embedding_size = embedding_size  # all-MiniLM-L6-v2 -> 384 dims natively

        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            self.model = SentenceTransformer(self.embedding_model_id)
        except Exception as e:
            self.logger.error(f"Failed to load local embedding model '{self.embedding_model_id}': {e}")
            self.model = None


    def set_generation_model(self, model_id: str):
        # this provider is embedding-only; kept for interface compatibility.

        raise NotImplementedError("this model not supported in generation")
     

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self._load_model()

    def construct_promot(self, message: str, role: str):
        # matches CohereProvider's typical shape: {"role": ..., "content": ...}
        return {"role": role, "content": message}

    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                       temperature: float = None):
        
        raise NotImplementedError("generate_text() is not supported by LocalEmbeddingProvider ")

     

    # ---- embedding-specific helpers ----

    def process_text(self, text: str) -> str:
   
        return text.strip().replace("\n", " ") if text else ""

    def embedd_text(self, text: str, document_type: str = None):
        """
        text: str for a single query, or list[str] for a batch of document chunks.
        document_type: kept only for interface compatibility with CohereProvider
                        (Cohere needs it to pick input_type=query/document;
                        local models don't need this distinction).
        """

        if self.model is None:
            self.logger.error("local embedding model not loaded")
            return None

        # normalize input to a list either way
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        texts = [self.process_text(t) for t in texts]

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
        except Exception as e:
            self.logger.error(f"Error while embedding text locally: {e}")
            return None

        embeddings = [vec[: self.embedding_size].tolist() for vec in embeddings]

        return embeddings if is_batch else embeddings[0]