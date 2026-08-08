
import os


class TempleteParser:

    def __init__(self, language: str, default_language: str = "en"):

        self.language = None
        self.default_language = default_language
        self.current_dir_path=os.path.dirname(os.path.abspath(__file__))
        self.set_language(language=language)


    def set_language(self,language:str):

        language_path=os.path.join(self.current_dir_path,"locales",language)
        if language is None:
            self.language=self.default_language

        if os.path.exists(language_path):
            self.language=language

        self.language=self.default_language

        return self.language

    def get(self,group:str,key:str,vars:dict=None):
        

        if group is None or key is None:
            return None
        target_language=self.language 
        
        group_path=os.path.join(self.current_dir_path,"locales",target_language,f"{group}.py")

        if not os.path.exists(group_path):
              target_language=self.default_language
              group_path=os.path.join(self.current_dir_path,"locales",target_language,f"{group}.py")

         
        module_name=__import__(f"templetes.locales.{target_language}.{group}" , fromlist=[group])   

        if not module_name:
            return None
               
        key_attribute=getattr(module_name,key)

        return key_attribute.substitute(vars)


    


        

       

        

