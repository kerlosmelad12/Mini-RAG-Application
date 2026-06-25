from .BaseControllers import BaseControllers
from fastapi import UploadFile
from models import ResponseValues

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