import db.mysql as Mysql
from models.config import *
import core.ahttp as AHttp
import logging
from tapdsdk.sdk import TapdAPIClient

class Tapd:
    def __init__(self,worspace_id=20427612):
        self.workspace_id = worspace_id
        self.sdk = TapdAPIClient(
            client_id="ymzx_py",
            client_secret="B72179EA-EBD3-7E5A-8E07-A22C3166F46F"
        )
        self.default = {'workspace_id': self.workspace_id}
    
    def getStoriesParamsList(self):
        info = self.sdk.get_story_fields_info(self.default)
        if info['status'] != 1:
            logging.getLogger('ERROR').error(f"get story fields info failed: {info['info']}")
            return {}
        else:
            return info['data']
        
    def getBugsParamsList(self):
        info = self.sdk.get_bug_fields_info(self.default)
        if info['status'] != 1:
            logging.getLogger('ERROR').error(f"get story fields info failed: {info['info']}")
            return {}
        else:
            return info['data']
        
    