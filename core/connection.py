from fastapi import Request,Response
import json

class Connection:
    def __init__(self,request: Request):
        self.request = request
    
    async def getRequestParams(self) -> dict:
        result = {}
        request = self.request
        if request.method == 'GET':
            result = request.query_params
        elif request.method == 'POST':
            result = await request.json()
        
        return dict(result)

    
    def success(self, params: dict) -> Response:
        return Response(json.dumps(params),media_type='application/json',status_code=200)

    def error(self, error_code: int, params: dict) -> Response:
        return Response(json.dumps(params),media_type='application/json',status_code=error_code)