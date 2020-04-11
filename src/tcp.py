import socket
import configparser
import os

class TcpRelay(object):
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