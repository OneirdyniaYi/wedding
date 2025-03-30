import core.ahttp as AHttp
import logging
from urllib.parse import urlparse

class GitWoa:
    def __init__(self):
        self.headers = {
            'accept' : '*/*',
            'PRIVATE-TOKEN' : 'G0gRZOKPQzV2U8r96Xcy'
        }
        self.apiUrl = 'https://git.woa.com/api/v3/projects/'
        
        
    async def getFileContent(self,repo,filePath,commitId):
        repoId = repo.replace('/','%2F')
        url = self.apiUrl + repoId + '/repository/blobs/' + commitId + '?filepath=' + filePath
        http = AHttp.AHttp()
        status,text = await http.get(url,headers=self.headers,isText=True)
        if status == 200:
            return text
        else:
            logging.getLogger('ERROR').error('get file content failed,url:%s,repo:%s,filePath:%s,commitId:%s,status:%s,text:%s' % (url,repo,filePath,commitId,status,text))
            return None
        
    async def getLatestCommitByFile(self,repo,branch,file):
        repoId = repo.replace('/','%2F')
        url = self.apiUrl + repoId + '/repository/branches/' + branch
        http = AHttp.AHttp()
        status,josn_res = await http.get(url,headers=self.headers)
        if status == 200:
            return josn_res['commit']['id']
        else:
            logging.getLogger('ERROR').error('get latest commit by branch failed,url:%s,repo:%s,branch:%s,status:%s,josn_res:%s' % (url,repo,branch,status,josn_res))
            return None
        
        