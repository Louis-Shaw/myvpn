import select
from constants import *
import logging

class EventLoop():
    def __init__(self):
        self.input_list = set()
        self.output_list = set()
        self.error_list = set()
        self._fdmap = {}

    def add_loop(self, conn, event, handle):
        fileno = conn.fileno()
        logging.info( 'add to loop :', fileno , event)
        if event == POLL_IN:
            self.input_list.add(fileno)
        if event == POLL_OUT:
            self.output_list.add(fileno)
        self.error_list.add(fileno)
        self._fdmap[fileno] = (conn, handle)

    def remove_loop(self, conn):
        fileno = conn.fileno()
        logging.info('remove loop', fileno)
        if fileno in self.input_list:
            self.input_list.remove(fileno)
        if fileno in self.output_list:
            self.output_list.remove(fileno)
        if fileno in self.error_list:
            self.error_list.remove(fileno)
        if fileno in self._fdmap:
            del self._fdmap[fileno]

    def restart_loop(self):
        logging.info('loop now', self.input_list)
        while True:
            rr, rw, re = select.select(self.input_list, self.output_list,
                self.error_list)
            if rr:
                logging.info('rr list' ,rr)
                for i in rr:
                    conn, handler = self._fdmap[i]
                    handler.handle_event(conn, POLL_IN)
            if rw:
                logging.info('rw')
                for i in rw:
                    conn, handle = self._fdmap[i]
                    handler.handle_event(conn, POLL_OUT)
            if re:
                logging.info('error')

    def close_sock(self, conn):
        self.remove_loop(conn)
        if conn.fileno():
            conn.close()