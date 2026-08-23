from .DataBaseModel import DataBaseModel
from .DB_Schemas.minirag.schemes.asset import Asset
from sqlalchemy.future import select
from typing import Optional


class AssetModel(DataBaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client=db_client

    
    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)
        return instance

 
    
    async def get_asset(self, asset_project_id: int, asset_name: str):

        async with self.db_client() as session:
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_name == asset_name
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
        return record
    
    async def insert_asset(self,asset:Asset):
       
       async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
       return asset   

    
    
    async def get_all_project_assets(self, asset_project_id: int, asset_type: Optional[str] = None):
        async with self.db_client() as session:
            conditions = [Asset.asset_project_id == asset_project_id]
            
            if asset_type is not None:
                conditions.append(Asset.asset_type == asset_type)
            
            stmt = select(Asset).where(*conditions)
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records
    
          

    

      
          
