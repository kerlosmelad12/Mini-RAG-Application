from enum import Enum 

class CoHereEnums(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = "search_document"
    QUERY = "search_query"    


class GrokEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMEnums(Enum):
    GROQ = "GROQ"
    COHERE = "COHERE"
    LOCALLLM="LOCALLLM"
