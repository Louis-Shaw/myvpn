import socket
import configparser
from constants import *
import os

class TcpRelay(object):
    self.local_conn = None
    self.remote_conn = None
    self.is_local = True

    def __init__(self, conn, is_local, loop):
        self.is_local = is_local
        self.local_conn = conn.fileno()
        self.loop = loop
        loop.add_loop(conn, POLL_IN)


    def handle_event(conn, event):
        if event == POLL_IN:
            if is_local:
                data = conn.recv(1024)
            
    def test(self):
        cf = configparser.ConfigParser()
        cf.read(os.path.split(os.path.realpath(__file__))[0] +
        '\config.conf')
        if cf.sections():
            local_ip = cf.get('local', 'local_ip')
            local_port = cf.get('local', 'local_port')
            print(local_ip, local_port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((local_ip, int(local_port)))
            sock.listen(1024)

            conn, addr = sock.accept()
            temp = conn.recv(1024)
            data = b''
            while temp:
                print(temp)
                data += temp
                temp = conn.recv(1024)
            print(data)







if __name__ == "__main__":
    tcp = TcpRelay()
    tcp.test()