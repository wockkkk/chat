import requests
from bot_config import *
import markdown
from bs4 import BeautifulSoup
from socket import *
import json
import re
import time

localhost = ['localhost', '127.0.0.1']

url = "https://api.siliconflow.cn/v1/chat/completions"
sys_tip = {"role": "system", "content": sys_tip}
payload = {
    "model": model_name,
    "messages": [],
    "max_tokens": 256
}
headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json"
}
re_compile = r'@\([^() ]+\) '

messages = []


def ai(messages):
    m_list = [sys_tip]
    for i in range(len(messages)):
        x = {"role": messages[i][0], "content": messages[i][1]}
        m_list.append(x)
        if i <= len(messages)-6:
            break
    payload['messages'] = m_list
    answer = requests.request("POST", url, json=payload, headers=headers).json()
    if answer.get('choices'):
        answer = answer['choices'][0]['message']['content']
        answer = BeautifulSoup(markdown.markdown(answer), 'html.parser').get_text()
    elif answer.get('code') == 50505:
        answer = '服务器繁忙，请稍后重试'
    elif type(answer) is str:
        answer = answer
    else:
        answer = answer.get('message', '未知错误')
    return answer


def recv_all(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        if len(chunk) < 4096:
            break
    return data


def main_loop():
    print('检测ing')
    s.sendall(json.dumps(['is_at', user_name]).encode())
    data = recv_all(s)
    data = json.loads(data)
    if data:
        print('被@')
        s.sendall(json.dumps(['get_message']).encode())
        message = recv_all(s)
        message: bytes
        message = json.loads(message)
        for message in message[::-1]:
            print(message)
            message: str
            match = re.findall(re_compile, message)
            if match:
                print(match)
                if match[0][2:-2] == user_name:
                    who, u_input = message.split(': ', 1)
                    print(who, u_input)
                    messages.append(('user',u_input))
                    return_word = f'@({who}) ' + ai(u_input)
                    messages.append(('',return_word))
                    print(return_word)
                    s.sendall(json.dumps(['send_message', return_word, account_id]).encode())
                    recv_all(s)
                    break


s = socket()
if server_ip in localhost:
    server_ip = gethostname()
s.connect((server_ip, server_port))
s.sendall(json.dumps(['signon', user_name, user_pwd]).encode())
d = json.loads(recv_all(s))
if d[0] == 'r':
    account_id = int(d[1])
else:
    print('用户未注册')
    exit()
while True:
    main_loop()
    time.sleep(1)
