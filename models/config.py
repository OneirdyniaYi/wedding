
from sqlmodel import Field, SQLModel
from pydantic import BaseModel,field_validator
from datetime import datetime
from typing import List
import json

class Config(SQLModel, table=True):
    id: int = Field(primary_key=True,default=None)
    fieldKey: str = Field(index=True,max_length=50)
    fieldType: int
    strContent: str | None = Field(default=None)
    tenant_id: str | None = Field(default=None)
    newFieldType: str | None = Field(default=None)
    
    
class YmzxExcelCompare(SQLModel, table=True):
    __tablename__ = 'ymzx_excel_compare'
    id: int = Field(primary_key=True,default=None)
    excel_name: str = Field(max_length=255)
    sheet_names: str | None = Field(default=None)
    compare_sheet_names: str | None = Field(default=None)
    self_branch: str
    compare_branch: str
    diff_infos: str | None = Field(default=None)
    self_commit: str | None = Field(default=None)
    compare_commit: str | None = Field(default=None)
    author: str | None = Field(default=None)
    date: datetime | None = Field(default=None)
    msg: str | None = Field(default=None)
    compare_author: str | None = Field(default=None)
    compare_date: datetime | None = Field(default=None)
    compare_msg: str | None = Field(default=None)
    full_path: str
    ctime: datetime
    
class YmzxExcelCompareRecord(SQLModel, table=True):
    __tablename__ = 'ymzx_excel_compare_record'
    id: int = Field(primary_key=True,default=None)
    excels: str = Field(default=None)
    self_branch: str
    compare_branch: str
    ctime: datetime
    rid: int
    is_finish: int = Field(default=0)
    pipeline_url: str

class TapdIterationDatas(SQLModel, table=True):
    __tablename__ = 'tapd_iteration_datas'
    id: int = Field(primary_key=True,default=0)
    name: str | None = Field(default=None)
    workspace_id: int
    description: str | None = Field(default=None)
    startdate: datetime | None = Field(default=None)
    enddate: datetime | None = Field(default=None)
    status: str | None = Field(default=None)
    creator: str | None = Field(default=None)
    created: datetime | None = Field(default=None)
    completed: datetime | None = Field(default=None)
    stories: str | None = Field(default=None)
    bugs: str | None = Field(default=None)
    stories_infos : str | None = Field(default=None)
    bugs_infos : str | None = Field(default=None)
    
class TapdDataInfos(SQLModel, table=True):
    __tablename__ = 'tapd_data_infos'
    id: int = Field(primary_key=True)
    type: str
    infos: str
    mtime: datetime
    
    
    
class ExcelCompareParams(BaseModel):
    excel_name: str
    sheet_names: list = []
    compare_sheet_names: list = []
    self_branch: str
    compare_branch: str
    diff_infos: dict = {}
    self_commit: str = ""
    compare_commit: str = ""
    author: str = ""
    date: str = ""
    msg: str = ""
    compare_author: str = ""
    compare_date: str = ""
    compare_msg: str = ""
    full_path: str
    
class ExcelCompareParamsRecord(BaseModel):
    self_branch: str
    compare_branch: str
    excels: list
    rid: str
    
class ExcelCompareParamsRecordQuery(BaseModel):
    rid: str

class ExcelOriginParams(BaseModel):
    commit: str
    full_path: str
    

class QRCodeParams(BaseModel):
    project: str
    pipelineId: str
    name: str
    webHook: str
    chatId: str
    
class BaseCIEventParams(BaseModel):
    before: str
    after: str
    ref: str
    user_name: str
    project_id: int

class BaseCIParams(BaseModel):
    projectId: str
    pipelineId: str
    event: BaseCIEventParams
    
class ModifyPipelineParams(BaseModel):
    pipeline_url: str
    params: dict
    type: str = 'add'
    
class GetPipelineParams(BaseModel):
    pipeline_url: str
    params: list
    
class GetPipelineParamsByHistory(BaseModel):
    pipeline_url: str
    params: list
    showNum: int = 1
    
class CurCompatibleParams(BaseModel):
    branch: str
    
class ExcelCompareApiParam(BaseModel):
    self_branch: str
    compare_branch: str
    excel: str
    rid: str
    full_path: str
    
class SetTapdIterationDatas(BaseModel):
    id: int
    name: str | None = None
    workspace_id: int
    description: str | None = None
    startdate: datetime | None = None
    enddate: datetime | None = None
    status: str | None = None
    creator: str | None = None
    created: datetime | None = None
    completed: datetime | None = None
    stories: list | None = None
    bugs: list | None = None
    stories_infos : dict | None = None
    bugs_infos : dict | None = None
    
    @field_validator('id', 'workspace_id', mode='before')
    def convert_str_to_int(cls, value):
        if isinstance(value, str):
            return int(value)
        return value
    
    @field_validator('stories', 'bugs','bugs_infos','stories_infos', mode='after')
    def parse_json(cls, value):
        return json.dumps(value)
    
    @field_validator('created', 'completed', mode='before')
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value

    @field_validator('startdate', 'enddate', mode='before')
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value
    
class SetTapdIterationDatasParam(BaseModel):
    datas: List[SetTapdIterationDatas]
    
class GetConfigSettings(BaseModel):
    fieldKey: str
    
class SetTapdDataInfos(BaseModel):
    id: int
    type: str
    infos: dict
    mtime: datetime | None = None
    
    @field_validator('id', mode='before')
    def convert_str_to_int(cls, value):
        if isinstance(value, str):
            return int(value)
        return value
    
    @field_validator('infos', mode='after')
    def parse_json(cls, value):
        return json.dumps(value)
    
    @field_validator('mtime', mode='before')
    def parse_datetime(cls, value):
        if isinstance(value, None):
            return datetime.now()
        elif isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value
    
class SetTapdDataInfosParam(BaseModel):
    datas: List[SetTapdDataInfos]
    
class GetFunctionResult(BaseModel):
    functions: list
    iteration_id: int