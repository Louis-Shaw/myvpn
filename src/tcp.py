import socket
import configparser
from constants import *
import os
import re

class TcpRelay(object):

    def __init__(self, conn, is_local, loop, config):
        self.is_local = is_local
        self.local_conn = conn
        self.buffer_size = 1024
        self.loop = loop
        self.config = config
        self.state = WAIT_TO_READ
        self.remote_conn = None
        loop.add_loop(conn, POLL_IN, self)

    def handle_local_read(self, conn):
        
        #read data
        #create remote conn
        #put conn into loop
        self.recv_all_data(conn)
        print( 'localdata ', self.data)
        self.loop.remove_loop(conn)
        if not self.remote_conn:
            remote_conn = self.create_remote_conn()
            self.loop.add_loop(remote_conn, POLL_OUT, self)
            self.remote_conn = remote_conn

    def create_remote_conn(self):

        if not self.data:
            #TODO raise exception
            return
        if not self.is_local:
            method, host, port = self.parse_header(self.data)
            res = socket.getaddrinfo(host, port)
            if len(res):
                fa, t, prtl, cn, addr = res[0]
                sock = socket.socket(fa, t, prtl)
                print('remote connect addr', addr)
                sock.connect(addr)
                return sock

        request_host = self.config.get('remote_ip', '')
        request_port = self.config.get('remote_port', '')
        res = socket.getaddrinfo(request_host, request_port)
        if len(res):
            fa, t, prtl, cn, addr = res[0]
            sock = socket.socket(fa, t, prtl)
            print('connect remote server', addr)
            sock.connect(addr)
            return sock


    def handle_local_write(self, conn):
        print(self.data)
        conn.sendall(self.data)
        print('send data done')
        self.loop.remove_loop(conn)

    def handle_remote_read(self, conn):
        self.recv_all_data(conn, False)
        self.loop.remove_loop(conn)
        self.loop.add_loop(self.local_conn, POLL_OUT, self)

    def handle_remote_write(self, conn):
        conn.sendall(self.data)
        self.loop.remove_loop(conn)
        self.loop.add_loop(conn, POLL_IN, self)

    def recv_all_data(self, conn, is_request=True):
        res = b''
        content_length = 0
        while True:
            temp_data = conn.recv(self.buffer_size)
            res += temp_data
            if b'\r\n\r\n' in temp_data:
                break
        self.data = res
        if is_request:
            return
        # read header complete
        # now parse out content-length
        reg = re.compile('^.*\\r\\n+Content-Length: (\d+)\\r\\n')
        groups = reg.search(res.decode('utf-8'))
       
        if groups:
            content_length = int(groups[1])
        while content_length > len(res):
            temp_data = conn.recv(self.buffer_size)
            res += temp_data
        
        self.data = res

            
    def handle_event(self, conn, event):
        print('tcp handle event', conn, event)
        conn_fileno = conn.fileno()
        if event == POLL_IN:
            if conn_fileno == self.local_conn.fileno():
                self.handle_local_read(conn)
            if conn_fileno == self.remote_conn.fileno():
                self.handle_remote_read(conn)
        if event == POLL_OUT:
            if conn_fileno == self.local_conn.fileno():
                self.handle_local_write(conn)
            if conn_fileno == self.remote_conn.fileno():
                self.handle_remote_write(conn)

    def parse_header(self, data):
        first_line = data.split(b'\r\n')[0]
        first_line = first_line.split(b' ')
        method = first_line[0]
        protocal, host , port= self.get_host(first_line[1])
        if not port:
            if 'https' in protocal:
                port = 443
            else:
                port = 80
        return (protocal, host, port)
    
    def get_host(self, host):
        reg = re.compile('(https?://)?([\w\.]+)[\:\/](\w*)')
        groups = reg.search(host.decode('utf-8'))
        if groups:
            return (groups[1], groups[2], groups[3])
        return ''
     
    def test(self):
        data = b'CONNECT vortex.data.microsoft.com:443 HTTP/1.1\r\nHost: vortex.data.microsoft.com\r\nConnection: close\r\n\r\n'
        res = self.parse_header(data)







if __name__ == "__main__":
        
    def get_host(host):
        reg = re.compile('(https?://)?([\w\.]+)[\:\/](\w*)')
        groups = reg.search(host.decode('utf-8'))
        print(groups)

        if groups:
            return (groups[1], groups[2], groups[3])
        return ''
    def parse_header(data):
        first_line = data.split(b'\r\n')[0]
        first_line = first_line.split(b' ')
        method = first_line[0]
        protocal, host, port = get_host(first_line[1])
        print(protocal)
        if not port:
            if 'https' in protocal:
                port = 443
            else:
                port = 80
        return (protocal, host, port)

    def test():
        data = b'CONNECT https://www.baidu.com/ HTTP/1.1\r\nHost: vortex.data.microsoft.com\r\n'
        res = parse_header(data)
        print(res)

    test()

