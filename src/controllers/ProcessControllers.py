from .ProjectControllers import ProjectControllers
from .BaseControllers import BaseControllers
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from typing import List, Optional
from dataclasses import dataclass
from models import DataTypeValues
from langchain_text_splitters import RecursiveCharacterTextSplitter

@dataclass
class Document:
    page_content: str
    metadata: dict


class ProcessControllers(BaseControllers):

    def __init__(self, project_id: str, sound_controller=None):
        super().__init__()
        self.project_id = project_id
        self.project_files_path = ProjectControllers().get_project_dir_file(project_id=project_id)
        self.project_sound_path = ProjectControllers().get_project_dir_sound(project_id=project_id)
        self.sound_controller = sound_controller

    def get_file_extention(self, file_id: str):
        return os.path.splitext(file_id)[-1]

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
        if self.sound_controller is None:
            return None

        sound_path = os.path.join(self.project_sound_path, sound_asset_name)
        result = self.sound_controller.transcribe(sound_path)

        if result is None or not result.get('text'):
            return None

        return [
            Document(
                page_content=result['text'],
                metadata={"source": sound_path}
            )
        ]

    def get_file_content(self, file_id: str, asset_type: str):
        if asset_type == DataTypeValues.FILE.value:
            loader = self.get_file_loader(file_id=file_id)
            if loader is None:
                return None
            return loader.load()
        elif asset_type == DataTypeValues.SOUND.value:
            return self.get_sound_loader(sound_asset_name=file_id)
        return None

  

    def process_file_content(self, file_content: list, file_id: str,
                          chunk_size: int = 600, overlap_size: int = 30,
                          ):

        file_content_texts = [self.clean_text(rec.page_content) for rec in file_content]
        file_content_metadata = [
            {**rec.metadata, "file_id": file_id} for rec in file_content
        ]

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size
        )

        for chunk in chunks:
            chunk_lang = self.detect_language(chunk.page_content)
            chunk.metadata["language"] = chunk_lang

        return chunks


    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict],
                                chunk_size: int, splitter_tag: str = "\n"):

        chunks = []

        # process each source document separately so its metadata stays attached
        for text, metadata in zip(texts, metadatas):
            lines = [line.strip() for line in text.split(splitter_tag) if len(line.strip()) > 1]

            current_chunk = ""

            for line in lines:
                current_chunk += line + splitter_tag
                if len(current_chunk) >= chunk_size:
                    chunks.append(Document(
                        page_content=current_chunk.strip(),
                        metadata=dict(metadata)  # copy, not shared reference
                    ))
                    current_chunk = ""

            # only append the leftover if it actually has content
            if len(current_chunk.strip()) > 0:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata=dict(metadata)
                ))

        return chunks