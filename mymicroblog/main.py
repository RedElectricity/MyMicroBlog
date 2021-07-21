'''
MyMicroBlog
============
Power By RedElectricity

Main APP
'''

__version__ = '0.1.0'
__author__ = 'RedElectricity'

#import need package
import json
from asyncio import sleep
from typing import List, Optional

import yaml
from fastapi import Cookie, FastAPI, File, Form, Request, Response, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from tinydb import TinyDB, where
from uvicorn import run
#import plugin
from .plugin import chat

#load config
config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
#Open Main Database file
db = TinyDB("mymicroblog/database.json")
#open content table
content = db.table("content")
#open comment table
comment = db.table("comment")

#defind how to encrypt token
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#defind main app
app = FastAPI(
    title=config['title'])

#export static file
app.mount("/static", StaticFiles(directory="mymicroblog/static"), name="static")
#load main templates folder
templates = Jinja2Templates(directory="mymicroblog/templates")

#load plugin router
app.include_router(chat.router)

@app.get("/")
async def MainPage(request: Request, token: Optional[str] = Cookie(None)):
    #load config
    config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
    #is login mode open?
    if config["mode"]["login"] == True:
        if token != config["token"]:
            #redirect to login page
            return RedirectResponse("/login")
        else:
            #render templates & return
            all_content = content.all()
            all_content.reverse()
            return templates.TemplateResponse("index.html", {"request": request,"title":config["title"],"author_info":{"author":config["author"],"author_description":config["author_description"],"author_description_short":config["author_description_short"],"contect":config["contect"]},"all_content":all_content,"theme_colour":config['theme_colour']})
    else:
        #render templates & return
        all_content = content.all()
        all_content.reverse()
        return templates.TemplateResponse("index.html", {"request": request,"title":config["title"],"author_info":{"author":config["author"],"author_description":config["author_description"],"author_description_short":config["author_description_short"],"contect":config["contect"]},"all_content":all_content,"theme_colour":config['theme_colour']})

@app.get("/info/{id}")
async def InfoPost(request: Request,id: int, token: Optional[str] = Cookie(None)):
    #
    config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
    if config["mode"]["login"] == True:
        if token != config["token"]:
            return RedirectResponse("/login")
        else:
            info_content = content.search(where("cid") == id)
            info_comment = comment.search(where("cid") == id)
            #print(info_content[0]["content"]["res"])
            result = {"request": request,"title":config["title"],"content": info_content[0],"comment":info_comment,"theme_colour":config['theme_colour']}
            return templates.TemplateResponse("info.html", result)
    else:
        info_content = content.search(where("cid") == id)
        info_comment = comment.search(where("cid") == id)
        #print(info_content[0]["content"]["res"])
        result = {"request": request,"title":config["title"],"content": info_content[0],"comment":info_comment,"theme_colour":config['theme_colour']}
        return templates.TemplateResponse("info.html", result)

@app.post("/comment/{id}")
async def AddComment(request: Request,id:int,username: str = Form(...),comment_content:str = Form(...)):
    comment.insert({"cid":id,"user":username,"content":comment_content})
    #return "提交成功"
    return templates.TemplateResponse("redirct.html", {"request":request,"info_message":"发布成功","return_address":f"/info/{id}","theme_colour":config['theme_colour']})

@app.get("/admin/")
async def admin(request: Request, token: Optional[str] = Cookie(None)):
    config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
    if token != config["token"]:
        return RedirectResponse("/login")
    else:
        all_content = content.all()
        all_content.reverse()
        result = {"request": request,"title":config["title"],"all_content":all_content,"theme_colour":config['theme_colour']}
        return templates.TemplateResponse("admin.html", result)

@app.get('/login/')
async def login(request: Request):
    result = {"request": request,"title":config["title"],"theme_colour":config['theme_colour']}
    return templates.TemplateResponse("login.html", result)

@app.post('/api/login/')
async def api_login(request:Request,password: str = Form(...), token : str = Cookie(None)):
    config = yaml.load(open('mymicroblog/config.yml','r',encoding="utf-8"),Loader=yaml.FullLoader)
    if password != config["password"]:
        return "密码错误"
    else:
        token = pwd_context.hash(password)
        config["token"] = token
        file = open('mymicroblog/config.yml','w',encoding="utf-8")
        file.write(str(yaml.dump(config)))
        await sleep(1)
        response = templates.TemplateResponse("redirct.html", {"request":request,"info_message":"登陆成功","return_address":f"/admin","theme_colour":config['theme_colour']})
        response.set_cookie(key="token",value=token)
        return response

@app.post("/api/push/")
async def api_push(request:Request,title:str = Form(...),push_content:str = Form(...),picture: Optional[List[UploadFile]] = File(...),video:Optional[UploadFile] = File(...)):
    video_list = []
    picture_list = []
    try:
        for image in picture:
            #print("add 1")
            name = str(image.filename)
            file = open(f"mymicroblog/static/image/{image.filename}",'wb')
            file.write((await image.read()))
            file.close()
        picture_list = [f"{image.filename}" for image in picture]
    except:
        pass

    try:   
        video_list.append(video.filename)
        file = open(f"mymicroblog/static/video/{video.filename}",'wb')
        file.write((await video.read()))
        file.close()
    except:
        pass

    all_content = content.all()
    all_content.reverse()
    try:
        cid = all_content[0]["cid"] + 1
    except:
        cid = 0
    content.insert({"cid":cid,"content":{"title":title,"content":push_content,"res":{"image":picture_list,"video":video_list}}})
    return templates.TemplateResponse("redirct.html", {"request":request,"info_message":"发布成功,返回查看","return_address":f"/info/{cid}","theme_colour":config['theme_colour']})

@app.get("/api/get_post/{id}")
async def api_get_post(id:int):
    try:
        return content.search(where("cid") == id)
    except:
        return "NO CONTENT FOUND"

@app.get("/api/del_post/{id}")
async def api_del_post(id:int):
    try:
        content.remove(where("cid") == id)
        return RedirectResponse(f"/admin")
    except:
        return "NO CONTENT FOUND"

if __name__ == "__main__":
    run(app=app,ip=config['host']['ip'],port=config['host']['port'])
