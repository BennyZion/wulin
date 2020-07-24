# -*- coding=utf-8 -*-
from socket import *
from threading import Thread,Lock
import struct
import time
class Location:
    def __init__(self, name, info, *args):
        self.npc = []
        self.player = []
        for i in args:
            self.npc.append(i)
        self.name = name
        self.info = info
class NPC:
    def __init__(self,name,hp,ad,say = '。。。。。',isatt = False):
        self.name = name
        self.hp = hp
        self.ad = ad
        self.isatt = isatt
        self.say = say

class Role:
    def __init__(self,name):
        self.name = name
        self.hp = 100
        self.ad = 10
        self.x = 1
        self.y = 1
        self.f =False
    def move(self,msg):
        if msg == 'cw':
            self.y += 1
        elif msg == 'cs':
            self.y -= 1
        elif msg == 'ca':
            self.x -= 1
        elif msg == 'cd':
            self.x += 1
        elif msg == 'cf':
            self.f =True

            pass
    pass
class Auth:
    def __init__(self,conn):
        self.conn = conn
    def login(self):
        global name_pw_dic
        while 1:
            self.conn.send('请输入用户名：'.encode('utf-8'))
            recv_name = self.conn.recv(1024).decode('utf-8').strip()
            if recv_name not in name_pw_dic:
                self.conn.send('用户不存在'.encode('utf-8'))
                continue
            else:
                while 1:
                    self.conn.send('请输入密码：'.encode('utf-8'))
                    recv_pw = self.conn.recv(1024).decode('utf-8').strip()
                    if recv_pw != name_pw_dic[recv_name]:
                        self.conn.send('密码错误！'.encode('utf-8'))
                        continue
                    else:
                        conn.send('登录成功！'.encode('utf-8'))
                        global live_player_li
                        live_player_li.append(recv_name)

                        return recv_name
    def register(self,lock):
        global name_pw_dic
        while 1:
            self.conn.send('请输入用户名：'.encode('utf-8'))
            recv_name = self.conn.recv(1024).decode('utf-8')
            if recv_name in name_pw_dic:
                self.conn.send('用户名已存在！'.encode('utf-8'))
                continue
            else:
                self.conn.send('请输入用户密码：'.encode('utf-8'))
                recv_pw = self.conn.recv(1024).decode('utf-8')
                with lock:
                    name_pw_dic[recv_name] = recv_pw
                    self.conn.send('注册成功！'.encode('utf-8'))
                    global live_player_li
                    live_player_li.append(recv_name)
                return recv_name
    def write(self):
        pass
    pass
def search(x,y):
    if x < 0 or x > 2 or y <0 or y > 2:
        return Map[1][1]
    else:
        return Map[x][y]
def Connect(conn,addr,lock):
    lg = Auth(conn)
    global name_pw_dic
    global live_player_li
    name = None
    while not name:
        conn.send('登录-l,注册-r：'.encode('utf-8'))
        recv_msg = conn.recv(1024).decode('utf-8')
        if recv_msg == 'l':
            name = lg.login()
        elif recv_msg == 'r':
            name = lg.register(lock)
        else:
            conn.send('请输入正确的操作'.encode('utf-8'))
    conn.send('seccessfullylogin'.encode('utf-8'))
    conn.recv(1024)#io阻塞，防止粘包
    print(f'玩家{name}已上线，ip_端口：{addr}')
    info = '''天下风云出我辈，

一入江湖岁月催。

皇图霸业谈笑中，

不胜人生一场醉 。

==========='''
    head_info = struct.pack('i', len(info))
    conn.send(head_info)
    conn.send(info.encode('utf-8'))
    conn.recv(1024)
    role = Role(name)
    while 1:
        print(f'玩家{name}坐标：[{role.x,role.y}]')
        this_map = Map[role.x][role.y]
        info = f'''当前你在{role.x, role.y},{this_map.name}
{this_map.info} 
你看到了：{[i.name for i in this_map.npc]} 
上：{search(role.x, role.y + 1).name}
下：{search(role.x, role.y - 1).name}
左：{search(role.x - 1, role.y).name}
右：{search(role.x + 1, role.y).name}
提示：w:↑ s:↓ a:← d:→ f:选择NPC
'''
        head_info = struct.pack('i', len(info))
        conn.send(head_info)
        conn.send(info.encode('utf-8'))
        recv_data = conn.recv(1024).decode('utf-8')
        role.move(recv_data)
        if role.f:
            while 1:
                npc_list = [i.name for i in this_map.npc]
                info = f'''请选择要交互的对象(输入序号)
                 {[i for i in npc_list]}
                '''
                head_info = struct.pack('i', len(info))
                conn.send(head_info)
                conn.send(info.encode('utf-8'))
                msg = conn.recv(1024).decode('utf-8')
                try:
                    if this_map.npc[int(msg[1:])].isatt:
                        pass
                    else:
                        info = f'{this_map.npc[int(msg[1:])].name}:{this_map.npc[int(msg[1:])].say}'
                        head_info = struct.pack('i', len(info))
                        conn.send(head_info)
                        conn.send(info.encode('utf-8'))
                        conn.recv(1024)  # io阻塞，防止粘包
                        role.f = False
                        break
                except:
                    continue
        if role.x < 0 or role.x > 2 or role.y <0 or role.y > 2:
            role.x, role.y = 1, 1
            info = '出界了，传送回新手村'
            head_info = struct.pack('i', len(info))
            conn.send(head_info)
            conn.send(info.encode('utf-8'))
            conn.recv(1024)  #io阻塞，防止粘包
            continue
        if role.hp < 0:
            print(f'玩家{name}阵亡')
            role.x,y = 1,1
            role.hp = 100
            info = '你已阵亡，已将你穿送回复活点'
            head_info = struct.pack('i', len(info))
            conn.send(head_info)
            conn.send(info.encode('utf-8'))
            conn.recv(1024)  # io阻塞，防止粘包

if __name__ == '__main__':
    mw = NPC('魔王',100,10,'人类，毁灭你，与你何干？')
    bfpp = NPC('白发婆婆',50,5,'"你现在正在一个岛上，名叫侠客岛，这里聚集了很多新入江湖的侠客，当然，也有一些是高手；你在这个岛上可以完成初级修炼。你现在先去侠客岛广场找一下侠客岛主，他会给你一些任务，你做完这些任务，就可以离开侠客岛，到风起云涌的江湖上去闯荡了！"')
    dz = NPC('岛主',100,20,'“当前的江湖风起云涌，五岳剑派与魔教势不两立；大理段氏的六脉神剑突现江湖；辟邪剑法、独孤九剑、九阳神功、乾坤大挪移、蛤蟆功、降龙十八掌，各种神功均要寻找传人，你也许有这个机缘。"')
    map1 = Location('荒野', '寒风凛冽，让你不时感到寒冷',mw)
    map0 = Location('新手村', '这里是勇士们的出生之地', bfpp,dz)
    Map = []
    for i in range(3):
        li = []
        for j in range(3):
            li.append(map1)
        Map.append(li)
    Map[1][1] = map0
    name_pw_dic = {
        'benny':'123456',
        'tony':'12456',
        '1':'1'
    }
    live_player_li = []
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('0.0.0.0', 8080))
    s.listen(5)
    lock = Lock()
    while 1:
        conn,addr = s.accept()
        t = Thread(target=Connect,args=(conn,addr,lock))
        t.start()


