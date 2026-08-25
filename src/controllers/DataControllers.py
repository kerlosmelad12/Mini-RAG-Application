from .BaseControllers import BaseControllers
from fastapi import UploadFile
from models import ResponseValues
from .ProjectControllers import ProjectControllers
import os
import re
from models import DataTypeValues

class DataControllers(BaseControllers):
    def __init__(self):          
        super().__init__()
        self.file_size = 1048576

    def validate_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_TYPE_EXTENTIONS: 
            return False,ResponseValues.NOT_APPROVED_TYPE.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.file_size:
            return False,ResponseValues.NOT_APPROVED_SIZE.value
        
        return True,ResponseValues.FILE_APPROVED.value

    def validate_sound(self, file: UploadFile):
            if file.content_type not in self.app_settings.SOUND_TYPE_EXTENSIONS:
                return False,ResponseValues.NOT_APPROVED_TYPE.value
            
            if file.size > self.app_settings.SOUND_MAX_SIZE * self.file_size:
                return False,ResponseValues.NOT_APPROVED_SIZE.value
            
            return True,ResponseValues.FILE_APPROVED.value
    
    def generate_filename(self,original_filename:str,project_id:str,file_type:str="file"):


        random_key=self.generate_random_string()

        if file_type==DataTypeValues.FILE.value:
            project_dir=ProjectControllers().get_project_dir_file(project_id)

        elif file_type==DataTypeValues.SOUND.value:
            project_dir=ProjectControllers().get_project_dir_sound(project_id)


        clean_filename=self.get_clean_file_name(
            original_filename
            )

        
        new_file_path=os.path.join(
                 project_dir,
                  random_key+"_"+ clean_filename  )
        
        while os.path.exists(new_file_path):
            random_key=self.generate_random_string()
            new_file_path=os.path.join(
                 project_dir,
                  random_key+"_"+ clean_filename )
            
        return new_file_path,random_key + "_" + clean_filename




        
    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
