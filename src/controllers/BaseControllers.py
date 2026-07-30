from helper.config import get_settings
import os
import random
import string
class BaseControllers:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir=os.path.dirname(os.path.dirname(__file__))
        self.file_dir=os.path.join(
            self.base_dir,
              'assests/Files'  )
    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))