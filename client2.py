# -*- coding=utf-8 -*-
from socket import *
import struct
s = socket(AF_INET,SOCK_STREAM)
s.connect(('127.0.0.1',8080))
Flag = True
while Flag:
    recv_msg = s.recv(1024).decode('utf-8')
    if recv_msg != 'seccessfullylogin':
        print(recv_msg)
        inp_msg = input('>>>')
        s.send(inp_msg.encode('utf-8'))
    else:
        s.send('111'.encode('utf-8'))#回应阻塞，防止粘包
        Flag = False
while 1:
    head_bytes = s.recv(4)
    head = struct.unpack('i',head_bytes)[0]
    recv_size = 0
    recv_data = b''
    while recv_size < head:
        eve_data = s.recv(1024)
        recv_data += eve_data
        recv_size += len(recv_data)
    print(recv_data.decode('utf-8'))
    inp_msg = 'c' + input('>>>#').strip()
    s.send(inp_msg.encode('utf-8'))

    pass
