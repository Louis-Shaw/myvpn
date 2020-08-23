import socket
import configparser
from constants import *
import os
import re
import logging

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

    def close_connections(self):
        if self.local_conn:
            self.loop.close_sock(self.local_conn)
        if self.remote_conn:
            self.loop.close_sock(self.remote_conn)

    def handle_local_read(self, conn):
        #read data
        #create remote conn
        #put conn into loop
        self.recv_all_data(conn)
        logging.info( 'localdata ', self.data)
        # remote local loop since After connection established, It will always
        # be ready to read and write.
        try:
            flag_443 = self.data.index(b'443')
        except:
            flag_443 = -1
        logging.info('flag', flag_443)
        self.loop.remove_loop(conn)
        # temporarily stop resolve Https request;
        if not self.remote_conn and flag_443 < 0:
            remote_conn = self.create_remote_conn()
            self.loop.add_loop(remote_conn, POLL_OUT, self)
            self.remote_conn = remote_conn
        else: 
            self.close_connections()

    def create_remote_conn(self):

        if not self.data:
            #TODO raise exception
            return
        if not self.is_local:
            import pdb;pdb.set_trace()
            method, host, port = self.parse_header(self.data)
            res = socket.getaddrinfo(host, port)
            if len(res):
                fa, t, prtl, cn, addr = res[0]
                sock = socket.socket(fa, t, prtl)
                logging.info('remote connect addr', addr)
                sock.connect(addr)
                return sock

        request_host = self.config.get('remote_ip', '')
        request_port = self.config.get('remote_port', '')
        res = socket.getaddrinfo(request_host, request_port)
        if len(res):
            fa, t, prtl, cn, addr = res[0]
            sock = socket.socket(fa, t, prtl)
            logging.info('connect remote server', addr)
            sock.connect(addr)
            return sock


    def handle_local_write(self, conn):
        logging.info(self.data)
        conn.sendall(self.data)
        logging.info('send data done')
        self.loop.remove_loop(conn)
        self.close_connections()

    def handle_remote_read(self, conn):
        self.recv_all_data(conn, False)
        self.loop.remove_loop(conn)
        self.loop.add_loop(self.local_conn, POLL_OUT, self)

    def handle_remote_write(self, conn):
        conn.sendall(self.data)
        self.loop.remove_loop(conn)
        self.loop.add_loop(conn, POLL_IN, self)

    def recv_all_data(self, conn, is_request=True):
        #import pdb;pdb.set_trace()
        header_length = 0
        res = b''
        content_length = 0
        while True and conn.fileno() > 0:
            temp_data = conn.recv(self.buffer_size)
            res += temp_data
            if b'\r\n\r\n' in temp_data:
                line_break_idx = res.index(b'\r\n\r\n')
                header_length = (line_break_idx + 4)
                break
        self.data = res
        #import pdb;pdb.set_trace()
        if is_request:
            return
        # read header complete
        # now parse out content-length
        reg = re.compile('^.*\\\\r\\\\n+Content-Length: (\d+)\\\\r\\\\n')
        groups = reg.search(str(res))
        if groups:
            content_length = int(groups[1]) + header_length
        while content_length > len(res) and conn.fileno() > 0:
            temp_data = conn.recv(self.buffer_size)
            res += temp_data
        
        self.data = res

            
    def handle_event(self, conn, event):
        logging.info('tcp handle event', conn, event)
        conn_fileno = conn.fileno()
        if event == POLL_IN:
            if self.local_conn and conn_fileno == self.local_conn.fileno():
                self.handle_local_read(conn)
            if self.remote_conn and conn_fileno == self.remote_conn.fileno():
                self.handle_remote_read(conn)
        if event == POLL_OUT:
            if self.local_conn and conn_fileno == self.local_conn.fileno():
                self.handle_local_write(conn)
            if self.remote_conn and conn_fileno == self.remote_conn.fileno():
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
        logging.info(groups)

        if groups:
            return (groups[1], groups[2], groups[3])
        return ''
    def parse_header(data):
        first_line = data.split(b'\r\n')[0]
        first_line = first_line.split(b' ')
        method = first_line[0]
        protocal, host, port = get_host(first_line[1])
        logging.info(protocal)
        if not port:
            if 'https' in protocal:
                port = 443
            else:
                port = 80
        return (protocal, host, port)

    def test():
        data = b'CONNECT https://www.baidu.com/ HTTP/1.1\r\nHost: vortex.data.microsoft.com\r\n'
        res = parse_header(data)
        logging.info(res)

    test()

