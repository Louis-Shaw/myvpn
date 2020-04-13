import socket
import configparser
import os
from eventloop import EventLoop

class Local:
    def __init__(self):
        cf = configparser.ConfigParser()
        cfpath = os.path.split(os.path.realpath(__file__))[0]+ '/config.conf'
        cf.read(cfpath)
        self.loop = None
        self.local_socket = None
        self.remote_socket = None
        self.local_ip = cf.get('local', 'local_ip')
        self.local_port = cf.get('local', 'local_port')
        self.remote_ip = cf.get('local', 'remote_ip')
        self.remote_port = cf.get('local', 'remote_port')
    
    def startLocal(self):
        print(self.local_ip, self.local_port, self.remote_ip, self.remote_port)
        local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local.setblocking(0)
        local.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local.bind((self.local_ip, int(self.local_port)))
        local.listen(1024)
        self.local_socket = local.fileno()
        self.loop = EventLoop()
        self.loop.addtoloop(local, self)
        self.loop.restartloop()

    def eventHandler(self, sock, event):
        if sock.fileno() == self.local_socket:
            # new a socket and put it in loop
            print('create accept')
            conn, addr = sock.accept()
            self.loop.addtoloop(conn, self)
        elif event == 'POLL_IN':
            data = sock.recv(1024)
            print(data)
            sock.sendall(b'HTTP/1.1 404 NOT FOUND')
            self.loop.close_sock(sock)
        elif event == 'POLL_OUT':
            sock.sendall(b'HTTP/1.1 404 NOT FOUND')


if __name__ == '__main__':
    lc = Local()
    lc.startLocal()