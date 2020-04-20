import socket
import configparser
import os
from eventloop import EventLoop
from tcp import TcpRelay

class Local:
    def __init__(self):
        cf = configparser.ConfigParser()
        cfpath = os.path.split(os.path.realpath(__file__))[0]+ '/config.conf'
        cf.read(cfpath)
        self.config = cf.sections('local')
        self.is_local = True
        self.loop = None
        self.local_socket = None
        self.local_ip = cf.get('local', 'local_ip')
        self.local_port = cf.get('local', 'local_port')


    def start_local(self):
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

    def handle_event(self, sock, event):
        if sock.fileno() == self.local_socket:
            # new a socket and put it in loop
            relay = TcpRelay(sock, is_local)
            print('create accept')
            conn, addr = sock.accept()
            self.loop.addtoloop(conn, self)

if __name__ == '__main__':
    lc = Local()
    lc.start_local()