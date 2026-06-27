from .BaseControllers import BaseControllers
import os
class ProjectControllers(BaseControllers):
    def __int__(self):
      super().__init__()

    def get_project_dir(self,project_id:str):
       project_dir=os.path.join(
          self.file_dir,
          project_id
          )

       if not os.path.exists(project_dir):
          os.makedirs(project_dir)
       return project_dir
      
       