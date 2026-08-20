from .ProjectControllers import ProjectControllers
from .BaseControllers import BaseControllers
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    page_content: str
    metadata: dict


class ProcessControllers(BaseControllers):
    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectControllers().get_project_dir(project_id=project_id)


    # get file extention 
    def get_file_extention(self,file_id:str):
       return os.path.splitext(file_id)[-1]
    

    # Load The file based on the extention
    def get_file_loader(self,file_id:str):
        file_path=os.path.join(self.project_path,
                     file_id)
        file_extention=self.get_file_extention(file_id)

        if file_path != None:

            if file_extention==ProcessingEnum.TXT.value:
                return TextLoader(file_path,encoding='utf-8')
        
            if file_extention == ProcessingEnum.PDF.value:
                return PyMuPDFLoader(file_path)
        
        return None
    # Load the file content
    def get_file_content(self,file_id:str):
        loader = self.get_file_loader(file_id=file_id)
        if loader ==None :
            return None
        return loader.load()
    
    # Process file conntect
    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20):
       
       file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

       file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        # chunks = text_splitter.create_documents(
        #     file_content_texts,
        #     metadatas=file_content_metadata
        # )

       chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size,
        )

       return chunks

    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        # split by splitter_tag
        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

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


    


    

                            




        
    
