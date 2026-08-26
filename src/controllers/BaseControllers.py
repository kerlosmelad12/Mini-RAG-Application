import os
import random
import string
import logging
import re
import unicodedata
from typing import Optional
from langdetect import detect, LangDetectException
from models.enums.AssetTypeEnum import Assetlanguadge  
from helper.config import get_settings

class BaseControllers:
    _keyword_model = None  # Singleton pattern for heavy KeyBERT model

    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir, 'assests/Files')
        self.sound_dir = os.path.join(self.base_dir, 'assests/Sounds')
        self.database_dir = os.path.join(self.base_dir, 'assests/Database')
        self.logger = logging.getLogger(__name__)

    def generate_random_string(self, length: int = 12) -> str:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_database_path(self, db_name: str) -> str:
        database_path = os.path.join(self.database_dir, db_name)
        os.makedirs(database_path, exist_ok=True)
        return database_path

    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        if not text or not text.strip():
            return None

        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        arabic_chars = len(arabic_pattern.findall(text))

        if arabic_chars > 0 and (arabic_chars / max(len(text), 1)) > 0.15:
            return Assetlanguadge.AR.value

        try:
            lang = detect(text)
            return Assetlanguadge.AR.value if lang == "ar" else Assetlanguadge.EN.value
        except LangDetectException:
            return None
        

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", text)
        text = "".join(
            char for char in text
            if char in "\n\t" or unicodedata.category(char)[0] != "C"
        )
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r'(?<=[\u0600-\u06FF])(?=[0-9])', ' ', text)
        text = re.sub(r'(?<=[0-9])(?=[\u0600-\u06FF])', ' ', text)
        return text.strip()