# MyMicroBlog

## 前言

这个是赤电酱无聊的时候做的啦,是一个微型博客的~~简单实现,没有加过多功能(这才一天做完欸)~~

竟然添加上了一个完整的chatroom,不可思议(

## 在使用之前

### 补全依赖

如果你使用poetry,那就好办辣,赤电最喜欢poetry辣,你只需执行以下这条指令:

```bash
poetry update
```

如果你用pip也没关系,只需要执行以下这条指令:

```bash
pip install fastapi[all]
```

### 你需要修改config.yml文件

在目录下有个`config.yml.examlp`,复原它,`config.yml`里面都有对应的注释辣,如果是正常人的话应该能看懂(

### 放置你的头像

把你的头像改成`author.png`,并扔到`static/image/`下

## 开始使用

### 启动!

你可以输入以下一条指令启动

```bash
uvicorn mymicroblog:app --port:80 --host:0.0.0.0
```

或者直接执行py文件也是可以哒~

### 操作~

在浏览器打开伺服器的ip地址+端口即可打开辣

右上角有个小按钮是管理面板

接下来就自己玩吧~

## 还有不足

> 毕竟一天就写完的project就不要要求太多辣(

- [x] Token还未加密
- [ ] Comment没有过滤
- [ ] 图片显示不整齐~~没有zoom out~~
- [x] 视频没有使用dplayer
- [ ] api没有验证
- [x] 页面跳转
- [ ] 图片显示有问题

## issue & pr

欢迎pr,issue最好按照以下格式

```
标题: [功能建议/BUG反馈] xxxx

功能建议的内容:
功能: xxxx
具体描述: xxxxx

bug反馈的功能:
使用OS: xxx
Python版本: xxxxxxx
日志: xxxxxx(用代码块)
控制台截图

```

在提交issue欠请务必按照<<提问的智慧>>提问!

## 关~于~

MyMicroBlog By RedElectricity Version 0.0.1



如果能赞助赤电酱就最好辣~

https://afdian.net/@RedElectricity