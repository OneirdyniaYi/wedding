from sqlmodel import SQLModel, select,update
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound,MultipleResultsFound
from urllib.parse import quote

import json
from typing import Type, Union, List, Optional, Dict
import logging 
import os
with open(os.path.join(os.path.dirname(__file__),'db_config.json'),'r') as f:
    data = json.load(f)
    host = data['host']
    password = data['password']
    database = data['database']
    user = data['user']
    port = data['port']
# password = quote('ZYQ5241@@')
# DATABASE_URL = f"mysql+aiomysql://root:{password}@9.134.130.69:3306/test"

DATABASE_URL = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"

engine = create_async_engine(DATABASE_URL, future=True,pool_recycle=28800,pool_pre_ping=True)
async_session = sessionmaker(expire_on_commit=False, class_=AsyncSession, bind=engine)

# async def register_database():
#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)
# async def get_db() -> AsyncSession:
#     async with SessionLocal() as session:
#         yield session


async def insert_and_update_datas(model: Type[SQLModel],data:List[dict]) -> bool:
    async with async_session() as session:
        try:
            for obj in data:
                model_instance = model(**obj)
                await session.merge(model_instance)
            await session.commit()
            return True,None
        except Exception as e:
            await session.rollback()
            logging.getLogger('ERROR').error(f"mysql insert_and_update_datas exec failed: {str(e)}")
            return False, str(e)

        

async def get_datas(
    model: Type[SQLModel],
    where: Dict, 
    one: bool = False
) -> Union[SQLModel, List[SQLModel]]:
    async with async_session() as session:
        try:
            statement = select(model)
            if where:
                statement = statement.where(*[getattr(model, k) == v for k, v in where.items()])
            if one:
                try:
                    result = await session.execute(statement)
                    return result.scalars().one(),None
                except NoResultFound:
                    logging.getLogger('WARNING').error(f"No result found for model {model}")
                    return None, "No result found"
                except MultipleResultsFound:
                    return result.scalars().first(),None
            result = await session.execute(statement)
            return result.scalars().all(),None
        except Exception as e:
            
            logging.getLogger('ERROR').error(f"mysql get_datas exec failed: {str(e)}")
            return None , str(e)


        
async def update_data(model: Type[SQLModel],where_conditions: Dict, new_values: Dict) -> bool:
    async with async_session() as session:
        try:
            stmt = update(model).where(*[getattr(model, k) == v for k, v in where_conditions.items()])
            await session.execute(stmt.values(**new_values))
            await session.commit()
            return True, None
        except Exception as e:
            await session.rollback()
            logging.getLogger('ERROR').error(f"mysql update exec failed: {str(e)}")
            return False , str(e)
        
        
async def insert(model: Type[SQLModel],data:List[SQLModel]) -> bool:
    async with async_session() as session:
        try:
            for obj in data:
                if not isinstance(obj, model):
                    raise ValueError(f"insert obj type is not {model}")
            session.add_all(data)
            await session.commit()
            return True,None
        except Exception as e:
            await session.rollback()
            logging.getLogger('ERROR').error(f"mysql insert exec failed: {str(e)}")
            return False , str(e)
        

