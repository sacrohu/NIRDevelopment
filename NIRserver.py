# coding: utf8
import socket
import select
import time
import sys


class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.inputs = []
        self.outputs = []
        self.exceptions = []

        self.iMessage = None
        self.oMessage = None

    def connectFrom(self):
        self.accepter = socket.socket()
        self.accepter.setblocking(False)
        self.accepter.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.accepter.bind((self.host, self.port))
        self.accepter.listen(10)

        self.inputs.append(self.accepter)
        self.exceptions.append(self.accepter)

        print(time.time(), "Socket accecpter Created", self.accepter.getsockname())

    def closeSocket(self, conn):
        try:
            print(time.time(), "Connection Closed", conn.getpeername())
        except Exception as e:
            print(time.time(), 'error of getpeername in close socket', e)

        if conn in self.inputs:
            self.inputs.remove(conn)
        if conn in self.outputs:
            self.outputs.remove(conn)
        if conn in self.exceptions:
            self.exceptions.remove(conn)
        conn.close()

    def handleSocketIO(self):
        try:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.exceptions, 1000)
            for r in readable:
                if r is self.accepter:
                    conn, addr = r.accept()
                    conn.setblocking(False)
                    self.inputs.append(conn)
                else:
                    try:
                        data = r.recv(1024)
                        if data:
                            self.iMessage = data
                            print(time.time(), "iMessage", data.hex(), r.getpeername())
                            self.dealSocket()
                        else:
                            self.closeSocket(r)
                    except socket.error as e:
                        print(time.time(), e, 'during reading [%s] .' % r)

            # error channel
            for e in exceptional:
                print(time.time(), 'exceptinal during select [%s] .' % e)
                self.closeSocket(e)
        except socket.error as e:
            print(time.time(), 'error in select', e)

    def dealSocket(self):
        self.iMessage = None

    def serverStart(self):
        try:
            self.connectFrom()
            print(time.time(), "Start Client Socket Local")
        except socket.error as e:
            print("Fail to Start Client Socket Local", e)


if __name__ == "__main__":
    print("监管群 启动，用于监管数据共享链的运行")
    client = Server("127.0.0.1", int(sys.argv[1]))    # 8729
    client.serverStart()

    while True:
        client.handleSocketIO()
