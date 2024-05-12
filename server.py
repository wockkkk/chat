import sqlite3
from socket import *
from threading import Thread
import time

messages = []
print('Server is running...')

close_server = False


def server(client: socket):
    global close_server
    r = ''
    spl = sqlite3.connect('user.sqlite')
    cur = spl.cursor()
    print('数据库加载完毕')
    while True:
        data = client.recv(1024).decode().split('|')
        if data[0] == 'signin':
            cur.execute(f"""insert into user(name, password, permission_level) values ('{data[1]}','{data[2]}',0)""")
            spl.commit()
            r = str(cur.execute(f"""select id from user where name = '{data[1]}'""").fetchall()[0][0])
        elif data[0] == 'signon':
            try:
                if data[2] == str(
                        cur.execute(f"""select password from user where name = '{data[1]}'""").fetchall()[0][0]):
                    r = ('r|' + str(
                        cur.execute(f"""select id from user where name = '{data[1]}'""").fetchall()[0][0]))
                else:
                    r = 'fuck'
            except IndexError:
                r = 'fuck'
        elif data[0] == 'get_message':
            if int(data[1]) == len(messages):
                r = '|'
            else:
                r = messages[int(data[1]) + 1]
        elif data[0] == 'send_message':
            if len(messages) == 50:
                messages.clear()
            messages.append(
                str(cur.execute(f"""select name from user where id = '{data[2]}'""").fetchall()) + ':' + data[1])
        elif data[0] == 'command':
            print(cur.execute(f"""select permission_level from user where id = {data[2]}""").fetchall())
            if data[1] == 'close':
                close_server = True
                break
        elif data[0] == '':
            break
        print(data)
        time.sleep(0.01)
        print(r)
        client.sendall(r.encode())
    client.close()
    cur.close()
    spl.close()


if __name__ == '__main__':
    s = socket()
    s.bind((gethostname(), 8080))
    s.listen(114)
    while True:
        client, addr = s.accept()
        t = Thread(target=server, args=(client,))
        t.setDaemon(True)
        t.start()
