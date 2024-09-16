import sqlite3
from socket import *
from threading import Thread

messages = []

chats = 0


def server(client: socket):
    global chats
    spl = sqlite3.connect('user.sqlite')
    cur = spl.cursor()
    print('数据库加载完毕')
    while True:
        r = ''
        try:
            data = client.recv(1024).decode().split('|')
        except ConnectionResetError:
            break
        if data[0] == 'signin':
            if not cur.execute(f"""select name from user where name = '{data[1]}'""").fetchall():
                cur.execute(
                    f"""insert into user(name, password, permission_level) values ('{data[1]}','{data[2]}',0)""")
                spl.commit()
                r = 'r|' + str(cur.execute(f"""select id from user where name = '{data[1]}'""").fetchall()[0][0])
            else:
                r = 'name error|'
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
                r = messages[int(data[1])]
        elif data[0] == 'send_message':
            if cur.execute(f"""select silence from user where id = {data[2]}""").fetchall()[0][0] == 1:
                continue
            if len(messages) == 50:
                messages.clear()
            say = cur.execute(f"""select name from user where id = '{data[2]}'""").fetchall()
            messages.append(str(say[0][0] + ':' + data[1]))
            print(messages)
        elif data[0] == 'command':
            if cur.execute(f"""select permission_level from user where id = '{data[2]}'""").fetchall()[0][0] >= 1:
                d = data[1].split(' ')
                if d[0] == 'silence':
                    cur.execute(f"""update user set silence = {d[2]} where name = '{d[1]}'""")
                if cur.execute(f"""select permission_level from user where id = '{data[2]}'""").fetchall()[0][0] == 2:
                    if d[0] == 'op':
                        op = d
                        if len(op) == 2:
                            permission_level = 1
                        elif op[2] == '2':
                            permission_level = 2
                        else:
                            continue
                        uid = cur.execute(f"""select id from user where name = '{d[1]}'""").fetchall()[0][0]
                        cur.execute(f"""update user set permission_level = {permission_level} where id = '{uid}'""")
                    if d[0] == 'ban':
                        cur.execute(f"""delete from user where name = '{d[1]}'""")

        elif data[0] == '':
            continue
        print(data)
        client.sendall(r.encode())
        print(r)
    chats -= 1
    client.close()
    cur.close()
    spl.close()


if __name__ == '__main__':
    s = socket()
    s.bind((gethostname(), 8080))
    print(f'bind:{(gethostname(), 8080)}')
    s.listen(114)
    print('Server is running...')
    while True:
        client, addr = s.accept()
        t = Thread(target=server, args=(client,))
        t.setDaemon(True)
        t.start()
        chats += 1
