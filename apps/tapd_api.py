from fastapi import APIRouter
import db.mysql as Mysql
from models.config import *
from classes.tapd import Tapd
from classes.custom_function import CustomFunction

Router = APIRouter(    
    prefix="/api/v1/tapd",
    tags=["tapd_api"],
    responses={404: {"description": "Not found"}},)

@Router.post("/setTapdIterationDatas")
async def setTapdIterationDatas(param: SetTapdIterationDatasParam):
    
    datas = []
    for data in param.datas:
        datas.append(data.__dict__)
    result,errorInfo = await Mysql.insert_and_update_datas(TapdIterationDatas,datas)
    
    if not result:
        return {'result':errorInfo,'msg':"fail"}
    return {'msg':"success"}

@Router.post("/getTapdStoriesParamsList")
async def getTapdStoriesParamsList():
    tapd = Tapd()
    res = tapd.getStoriesParamsList()
@Router.post("/getTapdBugsParamsList")
async def getTapdBugsParamsList():
    tapd = Tapd()
    res = tapd.getBugsParamsList()
    return {'msg':"success",'data':res}

@Router.post("/setTapdIterationDatas")
async def setTapdIterationDatas(param: SetTapdDataInfosParam):
    
    datas = []
    for data in param.datas:
        datas.append(data.__dict__)
    result,errorInfo = await Mysql.insert_and_update_datas(TapdDataInfos,datas)
    
    if not result:
        return {'result':errorInfo,'msg':"fail"}
    return {'msg':"success"}

@Router.post("/getFunctionResult")
async def getFunctionResult(param: GetFunctionResult):
    
    result,errorInfo = await Mysql.get_datas(TapdIterationDatas,{'id':param.iteration_id},True)
    
    if not result:
        return {'result':errorInfo,'msg':"fail"}

    cf = CustomFunction(result.stories_infos,result.bugs_infos)
    res = {}
    for funcItem in param.functions:
        count,desc = cf.calculate(funcItem['cfunction'])
        res[funcItem['title']] = {'count':count,'desc':desc}
    
    return {'msg':"success",'data':res}