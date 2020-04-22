import select
from constants import *

class EventLoop():
    def __init__(self):
        self.input_list = []
        self.output_list = []
        self.error_list = []
        self._fdmap = {}

    def add_loop(self, conn, event, handle):
        fileno = conn.fileno()
        print(fileno)
        if event == POLL_IN:
            self.input_list.append(fileno)
        if event == POLL_OUT:
            self.output_list.append(fileno)
        self.error_list.append(fileno)
        self._fdmap[fileno] = (conn, handle)

    def remove_loop(self, conn):
        fileno = conn.fileno()
        if fileno in self.input_list:
            self.input_list.remove(fileno)
        if fileno in self.output_list:
            self.output_list.remove(fileno)
        if fileno in self.error_list:
            self.error_list.remove(fileno)
        if self._fdmap.has_key(fileno):
            del self._fdmap[fileno]

    def restart_loop(self):
        print('loop now', self.input_list)
        while True:
            rr, rw, re = select.select(self.input_list, [], self.error_list)
            if rr:
                print('rr')
                for i in rr:
                    conn, handler = self._fdmap[i]
                    handler.eventHandler(conn, POLL_IN)
            if rw:
                print('rw')
                for i in rw:
                    conn, handle = self._fdmap[i]
                    handler.eventHandler(conn, POLL_OUT)
            if re:
                print('error')

    def close_sock(self, sock):
        self.removeloop(sock)