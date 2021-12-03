import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost",9001))
f = s.makefile(encoding='utf-8')

for l in f:
    print(l)