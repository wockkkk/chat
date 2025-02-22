# **一个简易的基于Python socket库的聊天程序**

### 1.库环境要求
机器人程序：requests, markdown, BeautifulSoup

客户端程序：PyQt5

服务端程序：sqlite3(python自带)
    
### 2.运行操作
1. 启动客户端及服务端：
  
    1. 启动服务器文件(server.py)
  
    2. 启动客户端(client.py)
    
    3. 选择有无账号
  
    4. 注册/登录(注：如连本机请在IP栏输127.0.0.1/localhost)
  
    5. 使用

2. 启动机器人：

    1. 修改配置(bot_config.py)尤其是api_key需改成自己的硅基流动apikey
  
    2. 启动机器人(AI user bot.py)
  
    3. 使用客户端@机器人账号 + 要说的话
  
    4. 自动回复

### 3.项目特点
可发送命令，如：

  1.禁言：silence *name \[0/1]
  
  2.给予/剥夺管理员：op *name * \[0/1/2]
  
  3.删除账号：ban *name
