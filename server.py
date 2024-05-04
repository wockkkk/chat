import sqlite3
from socket import *

spl = sqlite3.connect('user.sqlite')
cur = spl.cursor()
s = socket()
s.bind((gethostname(), 8080))
s.listen(5)
messages = []
print('Server is running...')
while True:
    client, addr = s.accept()
    print('Client connected:', addr)
    data = client.recv(1024).decode().split('|')
    print(data)
    if data[0] == 'signin':
        cur.execute(f"""insert into user(name, password, permission_level) values ('{data[1]}','{data[2]}',0)""")
        spl.commit()
        client.sendall(str(cur.execute(f"""select id from user where name = '{data[1]}'""").fetchall()[0][0]).encode())
    elif data[0] == 'signon':
        if data[2] == str(cur.execute(f"""select password from user where name = '{data[1]}'""").fetchall()[0][0]):
            client.sendall(('r|'+str(cur.execute(f"""select id from user where name = '{data[1]}'""").fetchall()[0][0])).encode())
    elif data[0] == 'get_message':
        if int(messages[1]) == len(messages)-1:
            client.sendall(''.encode())
        else:
            client.sendall(messages[int(data[1])+1].encode())
    elif data[0] == 'send_message':
        if len(messages) == 51:
            messages.pop(0)
        messages.append(str(cur.execute(f"""select name from user where id = '{data[2]}'""").fetchall())+':'+data[1])
    spl.commit()
cur.close()
spl.close()
