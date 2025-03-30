from fastapi import APIRouter,Response
from core.connection import Connection
from core.ahttp import AHttp
import db.mysql as Mysql
from models.config import Config,QRCodeParams
import json
import asyncio
import qrcode
from PIL import Image
import hashlib
import base64
import os
import io
from datetime import datetime

Router = APIRouter()

@Router.post("/qrcode")
async def qrcodeResponese(param: QRCodeParams) -> Response:
    project = param.project
    pipelineId = param.pipelineId
    name = param.name
    webHook = param.webHook
    chatId = param.chatId
    config,errorInfo = await Mysql.get_datas(Config,{'fieldKey':'landun_token'},True)
    header = {
            'content-type': 'application/json',
            'X-Bkapi-Authorization': json.dumps({
                "access_token": config.strContent
            })
    }
    
    http = AHttp()
    url = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/{project}/build_histories?pipelineId={pipelineId}&pageSize=20"
    status,resJson = await http.get(url, headers=header)
    if status != 200:
        print("GetBuildTemplateInstances failed..........")
        print(resJson)
    else:
        bot_header = {'content-type': 'application/json'}
        records = resJson['data']['records']
        if not records:
            return Response(json.dumps({'message': "没有找到相关记录"}),media_type='application/json',status_code=500)
        iosPath = None
        androidPath = None
        androidId = None
        iosId = None
        for record in records:
            if 'artifactList' not in record:
                continue
            artifactList = record['artifactList']
            available = False
            for artifact in artifactList:
                if artifact['name'].startswith('LetsGoServer'):
                    available = True
            if not available:
                continue
            for artifact in artifactList:
                if not iosPath and artifact['name'].endswith('enterprise_sign.ipa'):
                    iosPath = artifact['fullPath']
                    iosId = record['id']
                    iosStartTime = int(record['startTime']) / 1000
                elif not androidPath and artifact['name'].endswith('signed.apk'):
                    androidPath = artifact['fullPath']
                    androidId = record['id']
                    androidStartTime = int(record['startTime']) / 1000
            if iosPath and androidPath:
                break
        iosUrl = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/letsgo/artifactories/app_download_url?artifactoryType=CUSTOM_DIR&path={iosPath}"
        androidUrl = f"https://devops.apigw.o.woa.com/prod/v4/apigw-user/projects/letsgo/artifactories/app_download_url?artifactoryType=CUSTOM_DIR&path={androidPath}"
        if iosId == androidId:
            urlStr = f"https://devops.woa.com/console/pipeline/{project}/{pipelineId}/detail/{iosId}/outputs"
            # 将时间戳转换为datetime对象
            dt_object = datetime.fromtimestamp(iosStartTime)
            # 将datetime对象格式化为字符串
            formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            content = f"## 【{name}】- 最新可用构建包\n" \
           f"> #### 构建开始时间： <font color=\"info\">{formatted_time}</font>\n" \
           f"> #### [直达下载链接]({urlStr})\n" \
           f"> #### 您可扫描下面的二维码，<font color=\"warning\">依次获取安卓和IOS包</font>"
           
        else:
            iosStrURL = f"https://devops.woa.com/console/pipeline/{project}/{pipelineId}/detail/{iosId}/outputs"
            androidStrURL = f"https://devops.woa.com/console/pipeline/{project}/{pipelineId}/detail/{androidId}/outputs"
            dt_object = datetime.fromtimestamp(iosStartTime)
            formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            dt_object1 = datetime.fromtimestamp(androidStartTime)
            formatted_time1 = dt_object1.strftime("%Y-%m-%d %H:%M:%S")
            content = f"## 【{name}】- 最新可用构建包\n" \
           f"> #### 安卓构建开始时间： <font color=\"info\">{formatted_time1}</font>\n" \
           f"> #### [直达安卓下载链接]({androidStrURL})\n" \
           f"> #### IOS构建开始时间： <font color=\"info\">{formatted_time}</font>\n" \
           f"> #### [直达IOS下载链接]({iosStrURL})\n" \
           f"> #### 您可扫描下面的二维码，<font color=\"warning\">依次获取安卓和IOS包</font>"

        tasks = [http.get(androidUrl, headers=header),http.get(iosUrl, headers=header)]
        results = await asyncio.gather(*tasks)
        await http.post(webHook,headers=bot_header,data={'msgtype':'markdown','chatid':chatId,'markdown':{'content':content}})
        for key, response in enumerate(results):
            #print(response)
            if response[0] != 200:
                print(f"GetBuildTemplateInstances {response[1]}")
            else:
                resJson = response[1]
                qrUrl = resJson['data']['url']
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)

                qr.add_data(qrUrl)

                # 填充数据并生成二维码
                qr.make(fit=True)

                # 创建图片对象
                img = qr.make_image(fill_color="green", back_color="white")

                # 加载Logo图像
                logo = Image.open(os.path.join(os.path.dirname(__file__),'logo.png'))

                # 计算Logo的位置
                logo_width, logo_height = logo.size
                img_width, img_height = img.size
                logo_position = ((img_width - logo_width) // 2, (img_height - logo_height) // 2)

                # 将Logo嵌入二维码中
                img.paste(logo, logo_position)
                
                # 创建一个BytesIO对象，用于保存图像
                buffered = io.BytesIO()

                # 将图像保存为png格式的字节流
                img.save(buffered, format="PNG")

                # 获取字节流的二进制内容
                img_byte = buffered.getvalue()
                                
                base64_image = base64.b64encode(img_byte).decode('utf-8')
                md5_hash = hashlib.md5(img_byte).hexdigest()
                
                reqData = {
                    'msgtype' : "image",
                    'chatid' : chatId,
                    "image": {
                        "base64": base64_image,
                        "md5": md5_hash
                    }
                }
                #print(reqData)
                await http.post(webHook, headers=bot_header, data=reqData)
    return Response(json.dumps({'message': config.strContent}),media_type='application/json',status_code=200)

# @Router.route("/test",methods=['GET'])
# async def qrcode(request: Request) -> Response:
#     return Response('test',status_code=200)

# @Router.route("/api/v1/landun/get",methods=['GET'])
# async def qrcode(request: Request) -> Response:
#     return Response('test',status_code=200)

