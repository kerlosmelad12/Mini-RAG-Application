from .ProjectControllers import ProjectControllers
from .BaseControllers import BaseControllers
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from typing import List, Optional
from dataclasses import dataclass
from models import DataTypeValues


@dataclass
class Document:
    page_content: str
    metadata: dict


class ProcessControllers(BaseControllers):

    def __init__(self, project_id: str, sound_controller= None):
        super().__init__()
        self.project_id = project_id

        self.project_files_path = ProjectControllers().get_project_dir_file(project_id=project_id)

        self.project_sound_path = ProjectControllers().get_project_dir_sound(project_id=project_id)

        self.sound_controller = sound_controller

    # get file extension
    def get_file_extention(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    # Load the file based on the extension
    def get_file_loader(self, file_id: str):
        
        file_path = os.path.join(self.project_files_path, file_id)
        file_extention = self.get_file_extention(file_id)

        if file_path is not None:
            if file_extention == ProcessingEnum.TXT.value:
                return TextLoader(file_path, encoding='utf-8')

            if file_extention == ProcessingEnum.PDF.value:
                return PyMuPDFLoader(file_path)

        return None

    def get_sound_loader(self, sound_asset_name: str):

        print(f"DEBUG: self.sound_controller = {self.sound_controller}")   # 👈 جديد

        if self.sound_controller is None:
            print("DEBUG: sound_controller is None -> returning None")     # 👈 جديد
            return None

        sound_path = os.path.join(self.project_sound_path, sound_asset_name)
        print(f"DEBUG: sound_path = {sound_path}, exists = {os.path.exists(sound_path)}")   # 👈 جديد

        result = self.sound_controller.transcribe(sound_path)
        print(f"DEBUG: transcribe result = {result}")   # 👈 جديد

        if result is None or not result.get('text'):
            return None

        return [
            Document(
                page_content=result['text'],
                metadata={"source": sound_path}
            )
        ]

    # Load the file content based on asset type
    def get_file_content(self, file_id: str, asset_type: str):

        if asset_type == DataTypeValues.FILE.value:
            loader = self.get_file_loader(file_id=file_id)
            if loader is None:
                return None
            return loader.load()

        elif asset_type == DataTypeValues.SOUND.value:
            return self.get_sound_loader(sound_asset_name=file_id)

        return None

    # Process file content
    def process_file_content(self, file_content: list, file_id: str,
                              chunk_size: int = 100, overlap_size: int = 20):

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size,
        )

        return chunks

    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict],
                                  chunk_size: int, splitter_tag: str = "\n"):

        full_text = " ".join(texts)

        lines = [doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))
                current_chunk = ""

        if len(current_chunk) >= 0:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks