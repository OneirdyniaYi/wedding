import aiohttp

class AHttp:
    def __init__(self) -> None:
        pass
    
    async def post(self, url: str, data: dict={}, params: dict={},headers: dict={},isText = False) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, params=params, headers=headers,ssl=False) as response:
                if isText:
                    return response.status,await response.read()
                else:
                    return response.status,await response.json()
    
    async def get(self, url: str, data: dict={}, params: dict={},headers: dict={},isText = False) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json=data, params=params, headers=headers,ssl=False) as response:
                if isText:
                    return response.status,await response.read()
                else:
                    return response.status,await response.json()
                
    async def put(self, url: str, data: dict={}, params: dict={},headers: dict={},isText = False) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data, params=params, headers=headers,ssl=False) as response:
                if isText:
                    return response.status,await response.read()
                else:
                    return response.status,await response.json()

    
