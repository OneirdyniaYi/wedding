import core.ahttp as AHttp
import json
import logging
from urllib.parse import urlparse
import copy
import asyncio

class Landun:
    def __init__(self,token):
        self.headers={
            "X-Bkapi-Authorization": json.dumps({
                "access_token": token
            })
        }

    def _modify_validate_action(self,action):
        valid_actions = ["add", "delete","modify"]
        if action not in valid_actions:
            logging.getLogger("WARNING").warning(f"Invalid action: {action}. Expected one of: {valid_actions}")
            return False
        return True
    
    def compare_dicts(self,dict1, dict2):
        for key in set(dict1.keys()).union(dict2.keys()):
            if isinstance(dict1.get(key), dict) and isinstance(dict2.get(key), dict):
                self.compare_dicts(dict1.get(key), dict2.get(key))
            elif isinstance(dict1.get(key), list) and isinstance(dict2.get(key), list):
                self.compare_dicts(dict((i, v) for i, v in enumerate(dict1.get(key))), 
                            dict((i, v) for i, v in enumerate(dict2.get(key))))
            else:
                if dict1.get(key) != dict2.get(key):
                    logging.getLogger("INFO").info(f'Difference at {key}: {dict1.get(key)} vs {dict2.get(key)}')
                    
    async def modify_pipeline(self,url_list:list = [],params_dict:dict = {},type: str = 'add'):
        if not self._modify_validate_action(type):
            return
        http = AHttp.AHttp()
        
        ret = True
        
        for url in url_list:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            index = path_parts.index('pipeline')
            project = path_parts[index + 1]
            pipelineId = path_parts[index + 2]
            
            check_url = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/{project}/pipelines/pipeline_status?pipelineId={pipelineId}"
            status,check_json = await http.get(check_url,headers=self.headers)
            if status == 200 and check_json['status'] == 0:
                if check_json['data']['instanceFromTemplate'] == True:
                    logging.getLogger("DEBUG").debug(f"Pipeline {pipelineId} is an instance of a template")
                    pipelineName = check_json['data']['pipelineName']
                    templateId = check_json['data']['templateId']
                    template_param_url = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/{project}/build_manual_startup_info"
                    template_param = {
                        "pipelineId": pipelineId
                    }
                    status,template_param_json = await http.get(template_param_url, headers=self.headers, params=template_param)
                    logging.getLogger("DEBUG").debug(f"Template parameters: {template_param_json}")
                    params_old = template_param_json["data"]["properties"]
                    params_new = list(filter(lambda x: x['id'] != 'BK_CI_BUILD_MSG', params_old))
                    for param in params_new:
                        if param['id'] in params_dict:
                            if type == 'add':
                                if param['type'] == "STRING":
                                    if param['defaultValue'] == '':
                                        values = []
                                    else:
                                        values = param['defaultValue'].split(',')
                                    if params_dict[param['id']] not in values:
                                        values.append(params_dict[param['id']])
                                    param['defaultValue'] = ','.join(values)
                                elif param['type'] == "MULTIPLE":
                                    if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                        param['options'].append({
                                            "key":params_dict[param['id']],
                                            "value":params_dict[param['id']],
                                        })
                                    values = [str(item["value"]) for item in param['options']]
                                    param['defaultValue'] = ",".join(values)
                                elif param['type'] == "ENUM":
                                    if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                        param['options'].append({
                                            "key":params_dict[param['id']],
                                            "value":params_dict[param['id']],
                                        })
                                    param['defaultValue'] = params_dict[param['id']]
                            elif type == 'delete':
                                if param['type'] == "STRING":
                                    if param['defaultValue'] == '':
                                        values = []
                                    else:
                                        values = param['defaultValue'].split(',')
                                    param['defaultValue'] = ','.join([value for value in values if value != params_dict[param['id']]])
                                elif param['type'] == "MULTIPLE":
                                    for option in param['options']:
                                        if option['key'] == params_dict[param['id']]:
                                            param['options'].remove(option)
                                        values = [str(item["value"]) for item in param['options']]
                                        param['defaultValue'] = ",".join(values)
                                elif param['type'] == "ENUM":
                                    for option in param['options']:
                                        if option['key'] == params_dict[param['id']]:
                                            param['options'].remove(option)
                                        param['defaultValue'] = param['options'][0]["value"] if param['options'] else ''
                            elif type == 'modify':
                                if param['type'] == "STRING":
                                    param['defaultValue'] = params_dict[param['id']]
                                elif param['type'] == "MULTIPLE":
                                    if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                        param['options'].append({
                                            "key":params_dict[param['id']],
                                            "value":params_dict[param['id']],
                                        })
                                    values = [str(item["value"]) for item in param['options']]
                                    param['defaultValue'] = params_dict[param['id']]
                                elif param['type'] == "ENUM":
                                    if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                        param['options'].append({
                                            "key":params_dict[param['id']],
                                            "value":params_dict[param['id']],
                                        })
                                    param['defaultValue'] = params_dict[param['id']]
                    logging.getLogger("DEBUG").debug(f"New parameters: {params_new}")
                    update_url = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/{project}/templates/templateInstances"
                    update_params = {
                        "templateId": templateId,
                        "searchKey": pipelineName,
                    }
                    status,update_json = await http.get(update_url, headers=self.headers, params=update_params)
                    logging.getLogger("DEBUG").debug(f"Update response: {update_json}")
                    if status == 200 and update_json['status'] == 0:
                        lastVersion = update_json['data']['instances'][0]["version"]
                        logging.getLogger("INFO").info(f'modify_pipeline  lastVersion: {lastVersion}')
                        set_params = {
                            "templateId": templateId,
                            "version": lastVersion,
                        }
                        set_data = [{
                            "param":params_new,
                            "pipelineId": pipelineId,
                            "pipelineName": pipelineName,
                            "resetBuildNo":False,
                        }]
                        status,update_json = await http.put(update_url, headers=self.headers, params=set_params, data=set_data)
                        if status == 200 and update_json['status'] == 0:
                            logging.getLogger("DEBUG").debug(f"Update success: {update_json}")
                            logging.getLogger("INFO").info(f'modify_pipeline  template success')
                            continue
                    logging.getLogger("ERROR").error(f'modify_pipeline  template error,please check')
                    ret = False
                    continue
                logging.getLogger("DEBUG").debug(f"Pipeline {pipelineId} is not an instance of a template")
                get_url = f"https://devops.apigw.o.woa.com/prod/v3/apigw-user/projects/{project}/pipelines/{pipelineId}"
                
                status,josn_res = await http.get(get_url, headers=self.headers)
                if status == 200 and josn_res['status'] == 0:
                    data = josn_res['data']
                    oldData = copy.deepcopy(data)
                    for stage in data['stages']:
                        for container in stage['containers']:
                            if container['classType'] == 'trigger':
                                for param in container['params']:
                                    if param['id'] in params_dict:
                                        if type == 'add':
                                            if param['type'] == "STRING":
                                                if param['defaultValue'] == '':
                                                    values = []
                                                else:
                                                    values = param['defaultValue'].split(',')
                                                if params_dict[param['id']] not in values:
                                                    values.append(params_dict[param['id']])
                                                param['defaultValue'] = ','.join(values)
                                            elif param['type'] == "MULTIPLE":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                values = [str(item["value"]) for item in param['options']]
                                                param['defaultValue'] = ",".join(values)
                                            elif param['type'] == "ENUM":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                param['defaultValue'] = params_dict[param['id']]
                                        elif type == 'delete':
                                            if param['type'] == "STRING":
                                                if param['defaultValue'] == '':
                                                    values = []
                                                else:
                                                    values = param['defaultValue'].split(',')
                                                param['defaultValue'] = ','.join([value for value in values if value != params_dict[param['id']]])
                                            elif param['type'] == "MULTIPLE":
                                                for option in param['options']:
                                                    if option['key'] == params_dict[param['id']]:
                                                        param['options'].remove(option)
                                                    values = [str(item["value"]) for item in param['options']]
                                                    param['defaultValue'] = ",".join(values)
                                            elif param['type'] == "ENUM":
                                                for option in param['options']:
                                                    if option['key'] == params_dict[param['id']]:
                                                        param['options'].remove(option)
                                                    param['defaultValue'] = param['options'][0]["value"] if param['options'] else ''
                                        elif type == 'modify':
                                            if param['type'] == "STRING":
                                                param['defaultValue'] = params_dict[param['id']]
                                            elif param['type'] == "MULTIPLE":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                values = [str(item["value"]) for item in param['options']]
                                                param['defaultValue'] = params_dict[param['id']]
                                            elif param['type'] == "ENUM":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                param['defaultValue'] = params_dict[param['id']]
                    #self.compare_dicts(oldData,data)
                    status,resJson = await http.put(get_url,headers=self.headers,data=data)
                    
                    if status == 200 and resJson['status'] == 0:
                        continue
                    else: 
                        if resJson['status'] == 2101014:
                            status_url = f"https://devops.apigw.o.woa.com/prod/v3/apigw-user/projects/{project}/pipelines/{pipelineId}/status"
                            params_url = f"https://devops.apigw.o.woa.com/prod/v3/apigw-user/projects/{project}/pipelines/{pipelineId}/builds/manualStartupInfo"
                            tasks = [http.get(status_url, headers=self.headers),http.get(params_url, headers=self.headers)]
                            results = await asyncio.gather(*tasks)
                            for status_res,status_json in results:
                                if status_res == 200 and status_json['status'] == 0:
                                    if 'templateId' in status_json['data']:
                                        templateId = status_json['data']['templateId']
                                        versionId = status_json['data']['version']
                                    elif 'properties' in status_json['data']:
                                        params_list = status_json['data']['properties']
                                        
                            if params_list and templateId and versionId:
                                logging.getLogger("INFO").info(f"params_list: {params_list}")
                                logging.getLogger("INFO").info(f"templateId: {templateId}")
                                logging.getLogger("INFO").info(f"versionId: {versionId}")
                                for param in params_list:
                                    if param['id'] in params_dict:
                                        if type == 'add':
                                            if param['type'] == "STRING":
                                                if param['defaultValue'] == '':
                                                    values = []
                                                else:
                                                    values = param['defaultValue'].split(',')
                                                if params_dict[param['id']] not in values:
                                                    values.append(params_dict[param['id']])
                                                param['defaultValue'] = ','.join(values)
                                            elif param['type'] == "MULTIPLE":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                values = [str(item["value"]) for item in param['options']]
                                                param['defaultValue'] = ",".join(values)
                                            elif param['type'] == "ENUM":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                param['defaultValue'] = params_dict[param['id']]
                                        elif type == 'delete':
                                            if param['type'] == "STRING":
                                                if param['defaultValue'] == '':
                                                    values = []
                                                else:
                                                    values = param['defaultValue'].split(',')
                                                param['defaultValue'] = ','.join([value for value in values if value != params_dict[param['id']]])
                                            elif param['type'] == "MULTIPLE":
                                                for option in param['options']:
                                                    if option['key'] == params_dict[param['id']]:
                                                        param['options'].remove(option)
                                                    values = [str(item["value"]) for item in param['options']]
                                                    param['defaultValue'] = ",".join(values)
                                            elif param['type'] == "ENUM":
                                                for option in param['options']:
                                                    if option['key'] == params_dict[param['id']]:
                                                        param['options'].remove(option)
                                                    param['defaultValue'] = param['options'][0]["value"] if param['options'] else ''
                                        elif type == 'modify':
                                            if param['type'] == "STRING":
                                                param['defaultValue'] = params_dict[param['id']]
                                            elif param['type'] == "MULTIPLE":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                values = [str(item["value"]) for item in param['options']]
                                                param['defaultValue'] = params_dict[param['id']]
                                            elif param['type'] == "ENUM":
                                                if params_dict[param['id']] not in [item["value"] for item in param['options']]:
                                                    param['options'].append({
                                                        "key":params_dict[param['id']],
                                                        "value":params_dict[param['id']],
                                                    })
                                                param['defaultValue'] = params_dict[param['id']]
                                                
                                logging.getLogger("INFO").info(f"params_list: {params_list}")
                                
                                update_url = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/{project}/templates/templateInstances?templateId={templateId}&version={versionId}"
                                update_data = {
                                    'pipelineId':pipelineId,
                                    'param':params_list
                                }
                                update_status,update_json = await http.put(update_url,headers=self.headers,data=update_data)
                                if update_status == 200 and update_json['status'] == 0:
                                    continue
                                logging.getLogger("ERROR").error(f"update pipeline params failed: {update_json}")
                        ret = False
        return ret
                
        
    async def get_pipeline_params(self,url:str,params:list):
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        index = path_parts.index('pipeline')
        project = path_parts[index + 1]
        pipeline_id = path_parts[index + 2]
        
        get_url = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/{project}/build_manual_startup_info?pipelineId={pipeline_id}"
        http = AHttp.AHttp()
        status,josn_res = await http.get(get_url, headers=self.headers)
        if status == 200 and josn_res['status'] == 0:
            records = josn_res['data']['properties']
            res = {}
            for item in records:
                if item['id'] in params:
                    if item['type'] == "ENUM" or item['type'] == "MULTIPLE":
                        res[item['id']] = [option['value'] for option in item['options']]
                    else:
                        res[item['id']] = item['value']
            return res
        else:
            logging.getLogger("ERROR").error(f"get_pipeline_params failed: {josn_res}")
            return {}
        
    async def get_pipeline_params_by_history(self,url:str,params:list,showNum:int=1):
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        index = path_parts.index('pipeline')
        project = path_parts[index + 1]
        pipeline_id = path_parts[index + 2]
        
        get_url = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/{project}/build_histories?pipelineId={pipeline_id}&pageSize={showNum}"
        http = AHttp.AHttp()
        status,josn_res = await http.get(get_url, headers=self.headers)
        if status == 200 and josn_res['status'] == 0:
            records = josn_res['data']['records']
            res = {}
            for item in records:
                for param in item['buildParameters']:
                    if param['key'] in params:
                        res[item['id']] = {param['key']:param['value'],"buildNum":item['buildNum']}
            return res
        else:
            logging.getLogger("ERROR").error(f"get_pipeline_params failed: {josn_res}")
            return {}