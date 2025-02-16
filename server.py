import sqlite3
from socket import *
from threading import Thread
import json
from threading import Lock
import server_config
import re

messages = []
messages_lock = Lock()

online_users = {}  # 格式：{user_id: (name, permission_level)}
online_users_lock = Lock()

mentioned_users = []


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


def server(cli: socket):
    global online_users, mentioned_users
    spl = sqlite3.connect('user.sqlite')
    cur = spl.cursor()
    load = False
    print('数据库加载完毕')
    while True:
        r = []
        try:
            data = json.loads(recv_all(cli).decode())
        except (ConnectionResetError, json.decoder.JSONDecodeError):
            break
        if data[0] == 'get_message':
            r = messages
        elif data[0] == 'get_online_users':
            with online_users_lock:
                r = list(online_users.values())  # 返回格式：[('Alice', 1), ('Bob', 0)]
        elif data[0] == 'send_message':
            if cur.execute(f"""select silence from user where id = {data[2]}""").fetchall()[0][0] == 1:
                continue
            say = cur.execute(f"""select name from user where id = '{data[2]}'""").fetchall()
            new_message = say[0][0] + ': ' + data[1]
            matches = re.findall(r'@\(.+\) ', data[1])
            if matches:
                for name in matches:
                    name = name[2:-2]
                    mentioned_users.append(name)
            with messages_lock:
                messages.append(new_message)
            print(messages)
        elif data[0] == 'is_at':
            if data[1] in mentioned_users:
                mentioned_users.remove(data[1])
                r = [True]
            else:
                r = []
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
        elif data[0] == 'signin':
            if not cur.execute(f"""select name from user where name = '{data[1]}'""").fetchall():
                cur.execute(
                    f"""insert into user(name, password, permission_level) values ('{data[1]}','{data[2]}',0)""")
                spl.commit()
                r = ['r', str(cur.execute(f"""select id from user where name = '{data[1]}'""").fetchall()[0][0])]
            else:
                r = ['name error']
        elif data[0] == 'signon':
            try:
                if data[2] == str(
                        cur.execute(f"""select password from user where name = '{data[1]}'""").fetchall()[0][0]):
                    r = ['r', str(
                        cur.execute(f"""select id from user where name = '{data[1]}'""").fetchall()[0][0])]
                else:
                    r = ['password error']
            except IndexError:
                r = ["don't have this user"]
        elif data[0] == '':
            continue
        if data[0] in ('signin', 'signon') and r[0] == 'r':
            load = True
            user_id = int(r[1])
            user_name = cur.execute(f"select name from user where id={user_id}").fetchone()[0]
            perm_level = cur.execute(f"select permission_level from user where id={user_id}").fetchone()[0]
            with online_users_lock:
                online_users[user_id] = (user_name, perm_level)
        print(data)
        cli.sendall(json.dumps(r).encode())
        print(r, json.dumps(r).encode(), json.loads(json.dumps(r).encode()))
    if load:
        with online_users_lock:
            # noinspection PyUnboundLocalVariable
            if user_id in online_users:
                del online_users[user_id]
    cli.close()
    cur.close()
    spl.close()


if __name__ == '__main__':
    s = socket()
    s.bind((gethostname(), server_config.POST))
    print(f'bind:{(gethostname(), server_config.POST)}')
    s.listen(server_config.MAX_USER_NUM)
    print('Server is running...')
    while True:
        client, addr = s.accept()
        t = Thread(target=server, args=(client,))
        t.setDaemon(True)
        t.start()
