from fastapi import FastAPI
import uvicorn
from uvicorn.config import LOGGING_CONFIG
LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelprefix)s %(message)s"
import sys
import core.log as log

from db.mysql import engine,async_session
from apps import common,release_system,tapd_api
import os
import importlib

def load_routers_from_apps(apps_folder='apps'):
    routers = []
    # 获取 main.py 的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    apps_path = os.path.join(current_dir, apps_folder)
    # 获取 apps 文件夹中的所有文件
    for filename in os.listdir(apps_path):
        # 检查是否是 Python 文件
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]  # 去掉 .py 扩展名
            module_path = f"{apps_folder}.{module_name}"
            try:
                # 动态导入模块
                module = importlib.import_module(module_path)
                # 检查模块中是否有 Router 对象
                if hasattr(module, 'Router'):
                    routers.append(module.Router)
            except ImportError as e:
                print(f"Error importing {module_name}: {e}")
    return routers


app = FastAPI()
routers = load_routers_from_apps()
for router in load_routers_from_apps():
    print(router)
    app.include_router(router)


@app.on_event("startup")
async def startup_event():
    log.setup_loggers()
    print("Starting up")
    print(engine)
    print(async_session)

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down")
    





if __name__ == "__main__":
    
    config = uvicorn.Config(
        app,
        loop="auto",  # 事件循环实现
        limit_concurrency=1000,  # 并发限制
        timeout_keep_alive=30,  # keep-alive 超时
        host="127.0.0.1",
        port=8100,
        reload=True,
    )
    if sys.platform.startswith("linux"):
        config.loop = "uvloop"
        config.reload = False
    server = uvicorn.Server(config)
    server.run()