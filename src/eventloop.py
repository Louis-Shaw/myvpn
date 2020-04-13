import select


class EventLoop():
    def __init__(self):
        self.input_list = []
        self.output_list = []
        self.error_list = []
        self._fdmap = {}

    def addtoloop(self, conn, handle):
        fileno = conn.fileno()
        print(fileno)
        self.input_list.append(fileno)
        self.output_list.append(fileno)
        self.error_list.append(fileno)
        self._fdmap[fileno] = (conn, handle)
        self.restartloop()
        
    def removeloop(self, conn):
        fileno = conn.fileno()
        self.input_list.remove(fileno)
        self.output_list.remove(fileno)
        self.error_list.remove(fileno)
        self._fdmap[fileno] = None
        self.restartloop()

    def restartloop(self):
        print('loop now', self.input_list)
        while True:
            rr, rw, re = select.select(self.input_list, [], self.error_list)
            if rr:
                print('rr')
                for i in rr:
                    conn, handle = self._fdmap[i]
                    handle.eventHandler(conn, 'POLL_IN')
            if rw:
                print('rw')
                for i in rw:
                    conn, handle = self._fdmap[i]
                    handle.eventHandler(conn, 'POLL_OUT')
            if re:
                print('error')
    

    def close_sock(self, sock):
        self.removeloop(sock)