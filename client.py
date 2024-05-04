from socket import *
from threading import Thread

server_name = input('服务器IP?')
s = socket()
s.connect((server_name, 8080))
account = input('有没有账号?(y,n)')
message_index = 0

def get_message():
    global message_index
    while True:
        s.sendall(f'get_message|{message_index}'.encode())
        print(s.recv(1024).decode())
        if message_index <= 50:
            message_index += 1
        else:
            message_index = 0


if account == 'n':
    s.sendall(f"signin|{input('用户名?(不能有|)')}|{input('密码(不能有|)?')}".encode())
    account = s.recv(1024).decode()
elif account == 'y':
    s.sendall(f"signon|{input('用户名?(不能有|)')}|{input('密码(不能有|)?')}".encode())
    ohh = s.recv(1024).decode().split('|')
    if ohh[0] == 'r':
        account = ohh[1]
    else:
        print('6')
        exit()

else:
    print('???')
    exit()
Thread(target=get_message).start()
while True:
    s.sendall(f'send_message|{input('输入信息')}|{account}'.encode())

