from .DataBaseModel import DataBaseModel
from .enums import CollectionValues
from .DB_Schemas.project import Project

class ProjectModel(DataBaseModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.project_collection=db_client[CollectionValues.PROJECT_COLLECTION_NAME.value]

    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections=await self.db_client.list_collection_names()
        if CollectionValues.PROJECT_COLLECTION_NAME.value not in all_collections:
            self.project_collection=self.db_client[CollectionValues.PROJECT_COLLECTION_NAME.value]
            indexes=Project.get_indexes()
            for index in indexes:
                await self.project_collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )


    async def insert_project(self,project:Project):
        result= await self.project_collection.insert_one(project.dict(by_alias=True, exclude_unset=True))

        project.id=result.inserted_id  
        # Here will i get error because in pydantic schema treat with _id as a private

        return project
    
    async def get_or_create_one(self,project_id:str):
         result =await self.project_collection.find_one({"project_id":project_id})

         if result is None:
             project=Project(project_id=project_id)
             record=await self.insert_project(project)

             return record
         
         
    async def get_project(self, project_id: str):
        result = await self.project_collection.find_one(
            {"project_id": project_id}
        )

        if result:
            return Project(**result)

        return None

    
    async def get_all_projects(self,page:int=1,page_size:int=10):
        total_documents= await self.project_collection.count_documents({})


        total_pages=total_documents // page_size
        if total_documents % page_size>0:
            total_pages+=1

        cursor=self.project_collection.find().skip( (page-1) * page_size ).limit(page_size)
        projects=[]

        async for document in cursor:
            projects.append(
                Project(**document)
                            )
            
        return projects,total_pages
        

    

         


    

    
