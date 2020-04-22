import socket
import configparser
from constants import *
import os

class TcpRelay(object):

    def __init__(self, conn, is_local, loop, config):
        self.is_local = is_local
        self.local_conn = conn.fileno()
        self.loop = loop
        self.config = config
        self.state = WAIT_TO_READ
        self.remote_conn = None
        loop.add_loop(conn, POLL_IN, self)

    def handle_local_read(self, conn):
        #read data
        #create remote conn
        #put conn into loop
        self.data = conn.recv(1024)
        print(self.data)
        if not self.remote_conn:
            self.create_remote_conn()
        self.loop.remove_loop(conn)
        self.loop.add_loop(self.remote_conn, POLL_OUT, self)

    def create_remote_conn(self):
        request_host = self.config.remote_ip
        request_port = self.config.remote_port
        if not is_local:
            request_host = 'www.baidu.com'
            request_port = 80
        if not self.data:
            #TODO raise exception
            return
        res = socket.getaddrinfo(request_host, request_port)
        if len(res):
            fa, t, prtl, cn, addr = res[0]
            sock = socket.socket(fa, t, prtl)
            rmt_conn = sock.connect(addr)
            self.remote_conn = rmt_conn

    def handle_local_write(self, conn):
        conn.sendall(self.data)
        self.loop.remove_loop(conn)
        self.loop.add_loop(conn, POLL_IN, self)

    def handle_remote_read(self, conn):
        self.data = conn.recv(1024)
        self.loop.remove_loop(conn)
        self.loop.add_loop(self.local_conn, POLL_OUT, self)

    def handle_remote_write(self, conn):
        conn.sendall(self.data)
        self.loop.remove_loop(conn)
        self.loop.add_loop(self.remote_conn, POLL_IN, self)

    def handle_event(self, conn, event):
        conn_fileno = conn.fileno()
        if event == POLL_IN:
            if conn_fileno == self.local_conn:
                self.handle_local_read(conn)
            if conn_fileno == self.remote_conn:
                self.handle_remote_read(conn)
        if event == POLL_OUT:
            if conn_fileno == self.local_conn:
                self.handle_local_write(conn)
            if conn_fileno == self.remote_conn:
                self.handle_remote_write(conn)
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