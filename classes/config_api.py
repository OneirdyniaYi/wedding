import db.mysql as Mysql
from models.config import *
import json

class ConfigApi:
    def __init__(self):
        pass
    
    async def getSettings(self,param:str):
        config,errorInfo = await Mysql.get_datas(Config,{'fieldKey':param},True)
        if config:
            if config.newFieldType == 'atc':
                return config.strContent.split(';'),config.newFieldType
            elif config.newFieldType in ['twoDimensionalArray','multiSelect','oneDimensionalArray']:
                return json.loads(config.strContent),config.newFieldType
            elif config.newFieldType in ['input','textarea','string']:
                return config.strContent or "",config.newFieldType
            elif config.newFieldType == 'switch':
                return True if config.strContent == '1' else False,config.newFieldType
        else:
            return None,None