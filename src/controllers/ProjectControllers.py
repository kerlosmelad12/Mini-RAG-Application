from .BaseControllers import BaseControllers
import os

class ProjectControllers(BaseControllers):
    def __init__(self):
        super().__init__()

    def get_project_dir_file(self, project_id: int):
        project_dir = os.path.join(self.file_dir, str(project_id))
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir

    def get_project_dir_sound(self, project_id: int):
        project_dir = os.path.join(self.sound_dir, str(project_id))
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir