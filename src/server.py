import socket
import configparser
import os
from eventloop import EventLoop
from tcp import TcpRelay
from constants import *

class Server(object):
    def __init__(self):
    cf = configparser.ConfigParser()
    cfpath = os.path.split(os.path.realpath(__file__))[0]+ '/config.conf'
    cf.read(cfpath)
    self.config = cf.sections('server')
    self.is_local = True
    self.loop = None
    self.local_socket = None
    self.local_ip = cf.get('server', 'local_ip')
    self.local_port = cf.get('server', 'local_port')

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.local_ip , self.local_port))
        server.listen(1024)
        self.server_socket = server.fileno()
        self.loop = EventLoop()
        self.loop.add_loop(server, self)
        self.loop.restart_loop()

    def handle_event(self, sock, event):
        if sock.fileno() == self.server_socket
            relay = TcpRelay(sock, is_local)
            print('server create accept')
            conn, addr = sock.accept()
            self.loop.add_loop(conn, POLL_IN)


if __name__ == '__main__':
    server = Server()
    server.start_server()