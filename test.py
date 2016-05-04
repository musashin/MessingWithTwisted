__author__ = 'nulysse'
import socket
import threading

consolemutex = threading.Lock()

listening_port = 7000

class UDPServer:
    def __init__(self):
        self.s=None
        self.t=None
    def start(self, port, servername):
        if not self.s:
            self.s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind(("",port))
            self.t=threading.Thread(target=self.run)
            self.t.start()
            self.readport = port
            self.servername = servername
    def stop(self):
        if self.s:
            self.s.close()
            self.t.join()
            self.t=None
    def run(self):
        while True:
            try:
                #receive data
                data,addr=self.s.recvfrom(1024)
                self.onPacket(addr,data)
            except:
                break
        self.s= None

    def onPacket(self,addr,data):
        consolemutex.acquire()
        print '----'
        print '{!s} [port {!s}]'.format(self.servername,self .readport)
        print 'data is {!s} [raw is {!s}]'.format(data, ":".join("{:02x}".format(ord(c)) for c in data))
        consolemutex.release()

Sendsocket = socket.socket(   socket.AF_INET, # Internet
                              socket.SOCK_DGRAM) # UDP

if __name__ == '__main__':

    GUIListener = UDPServer()
    GUIListener.start(listening_port, 'SimHostListen')

    while True:
        raw_input("Press a key to send a message...")

        Sendsocket.sendto("Hello", ('127.0.0.1', 6007))

