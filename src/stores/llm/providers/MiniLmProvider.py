import logging
from stores.llm.LLMInterface import LLMInterface
from sentence_transformers import SentenceTransformer


class LocalEmbeddingProvider(LLMInterface):

    def __init__(self, model_name, input_defualt_max_characters: int = 1024):
        self.model_name = model_name
        self.tokenizer = SentenceTransformer(self.model_name)
        self.input_defualt_max_characters = input_defualt_max_characters
        self.embedding_size = self.tokenizer.get_sentence_embedding_dimension()
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        raise NotImplementedError("this model not supported in generation")

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.model_name = model_id
        self.embedding_size = embedding_size
        self.tokenizer = SentenceTransformer(self.model_name)

    def construct_promot(self, message: str, role: str):
        raise NotImplementedError("this function not supported in LocalEmbedding Provider")

    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                       temperature: float = None):
        raise NotImplementedError("this function not supported in LocalEmbedding Provider")

    def process_text(self, text: str):
        return text[0:self.input_defualt_max_characters].strip()

    def embedd_text(self, text, document_type: str = None):

        if self.tokenizer is None:
            self.logger.error("local embedding model not loaded")
            return None

        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        texts = [self.process_text(t) for t in texts]

        try:
            embeddings = self.tokenizer.encode(texts, convert_to_numpy=True  , batch_size=64)
        except Exception as e:
            self.logger.error(f"Error while embedding text locally: {e}")
            return None

        embeddings = [vec[: self.embedding_size].tolist() for vec in embeddings]

        return embeddings if is_batch else embeddings[0]