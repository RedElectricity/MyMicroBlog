__version__ = "0.1.0"

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Cookie, Form
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
import yaml
from typing import List, Optional
from uuid import uuid4 as uuid
import json
from PIL import Image
from io import BytesIO
from tinydb import TinyDB, Query, where

router = APIRouter()
templates_plugin = Jinja2Templates(directory="mymicroblog/templates/plugin/chat")
templates = Jinja2Templates(directory="mymicroblog/templates")

db = TinyDB('mymicroblog/chat.json')
chat_db = db.table("chat")

config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)



manager = ConnectionManager()


@router.get("/chat")
async def chat_main(request: Request,chat_username: str = Cookie(None)):
    if chat_username == None:
        return RedirectResponse("/chat/login")
    else:
        config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
        if config["plugin"]["chat"] == True:
            result = {"request": request,"title":config["title"],"full_url":config["host"]["full_url"],"chat_username":chat_username,"theme_colour":config['theme_colour']}
            return templates_plugin.TemplateResponse("main.html", result)
        else:
            return templates.TemplateResponse("redirct.html", {"request":request,"info_message":"Chat插件未开启","return_address":f"/","theme_colour":config['theme_colour']})

@router.get("/chat/login")
async def chat_login(request: Request):
    config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
    return templates_plugin.TemplateResponse('login.html',{"request": request,"title":config["title"],"theme_colour":config['theme_colour']})

@router.post('/chat/api/login/')
async def chat_api_login(request:Request,username: str = Form(...), chat_username : str = Cookie(None)):
    response = templates.TemplateResponse("redirct.html", {"request":request,"info_message":"设定成功","return_address":f"/chat","theme_colour":config['theme_colour']})
    response.set_cookie(key="chat_username",value=username)
    return response

@router.get("/chat/api/message/clean")
async def chat_login(request: Request,token: Optional[str] = Cookie(None)):
    config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
    if token != config["token"]:
        return RedirectResponse("/login")
    else:
        chat_db.truncate()
        return "SUCCESSFUL!"


@router.post("/chat/push")
async def chat_plf(request:Request,picture: bytes = File(...)):
    if len(picture) != 0:
        #extension = picture.filename.split(".")[-1] in ("jpg", "jpeg", "png")
        #if not extension:
        #    return "Image must be jpg or png format!"
        filename = str(uuid()) + ".jpg"
        #print(picture.filename)
        image = read_image(picture)
        image.thumbnail((256,256))
        image.save(f'mymicroblog/static/image/chat/{filename}')
        return {"file_name":filename}
    else:
        {"error":"文件损坏"}


@router.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    for times in range(10):
        try:
            #print(f"Recall {times + 1}:{chat_list[times]}")
            await manager.send_personal_message(json.dumps(chat_db.all()[times]), websocket)
        except:
            break
    await manager.broadcast(json.dumps({"event":"join","message":f"#{client_id} 加入了聊天室"}))
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data['picture'] == "":
                result = {"event":"talk","user":f"#{client_id}","message":f"{data['message']}"}
                chat_db.insert(result)
                await manager.broadcast(json.dumps(result))
            else:
                result = {"event":"talk","user":f"#{client_id}","message":f"{data['message']}","picture":f"http://{config['host']['full_url']}/static/image/chat/{data['picture']}"}
                chat_db.insert(result)
                await manager.broadcast(json.dumps(result))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"event":"leave","message":f"#{client_id} 离开了聊天室"}))

def read_image(file) -> Image.Image:
    result = Image.open(BytesIO(file)).convert('RGB')
    return result