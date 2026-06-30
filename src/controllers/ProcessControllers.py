from .ProjectControllers import ProjectControllers
from .BaseControllers import BaseControllers
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum

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

        if file_extention==ProcessingEnum.TXT.value:
            return TextLoader(file_path,encoding='utf-8')
        
        if file_extention == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None
    # Load the file content
    def get_file_content(self,file_id:str):
        loader = self.get_file_loader(file_id=file_id)
        return loader.load()
    
    # Process file conntect
    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20):
       
       text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )
       file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

       file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]
       
       chunks = text_splitter.create_documents(
       file_content_texts,
       metadatas=[
        {
            **metadata,
            "file_id": file_id
        }
        for metadata in file_content_metadata
           ]
          )
       return chunks

                            




        
    
