__author__ = 'nulysse'

import ConfigParser
from twisted.internet import protocol, reactor, defer
from Tkinter import *
from twisted.internet import tksupport
root = Tk()
tksupport.install(root)


_SimHostListenPort = 6007
_GUI_send_port = 7000


class TestMessages(object):
    """
    This class handles parsing of the INI file containing the list of messages
    """
    def __init__(self, configFile):

        config = ConfigParser.RawConfigParser()
        config.read(configFile)

        sections = config.sections()

        self.request_list = list()
        for section in sections:
            self.request_list.append(config.get(section, 'request_file'))


class RemoteDebuggerGUI(protocol.DatagramProtocol):

    def __init__(self, receivedMsgList):
        self.receivedMsgList = receivedMsgList

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        self.receivedMsgList.insert(0, "Received Message")

    def write(self, data, host, port):
        self.transport.write(data, (host, port))


class TesterFrame(Frame):
    '''
    This class implements the GUI for the tester application
    '''

    def __init__(self, master, font, testMessages):
        ''' Sets up the gui, callback, and widget handles '''
        Frame.__init__(self, master)

        self.testMessages = testMessages.request_list
        #---------------------------------------------------------------------------#
        # Initialize Buttons Handles
        #---------------------------------------------------------------------------#
        frame = Frame(self)
        frame.pack(side=BOTTOM, pady=5)

        self.availablemessagelistbox = Listbox(master)
        self.availablemessagelistbox.pack(side=LEFT, padx=15, fill="both", expand=True)

        for request in testMessages.request_list:
            self.availablemessagelistbox.insert(END, request)

        self.selectedmessagelistbox = Listbox(master)
        self.selectedmessagelistbox.pack(side=LEFT, padx=15, fill="both", expand=True)

        self.sendButton = Button(frame, text="send", command=self.send_clicked, font=font)
        self.sendButton.pack(side=BOTTOM, padx=15)

        self.addButton = Button(frame, text="add", command=self.add_message_to_send, font=font)
        self.addButton.pack(side=BOTTOM, padx=15)

        self.receivedMsg = Entry(master)
        self.receivedMsg.pack(side=BOTTOM, padx=15, fill="both", expand=True)



        self.guiEmulator = RemoteDebuggerGUI(self.receivedMsg)
        reactor.listenUDP(_SimHostListenPort, self.guiEmulator)


    def add_message_to_send(self):
        indexes = self.availablemessagelistbox.curselection()
        selectedmessages = [self.testMessages[int(index)] for index in indexes]

        for msg in selectedmessages:
            self.selectedmessagelistbox.insert(END, msg)

    def send_clicked(self):
        print 'Sending {!s} message'.format(len(self.selectedmessagelistbox.get(0, END)))

        for msgFile in self.selectedmessagelistbox.get(0, END):
            with open(msgFile, 'rb') as msgData:
                self.guiEmulator.write(msgData.read(), '127.0.0.1', _GUI_send_port)


class TesterApplication(object):
    ''' The main Tkinter application handle for our Tester Application
    '''

    def __init__(self, master, testMessages):
        '''
        Called by wxWindows to initialize our application

        :param master: The master window to connect to
        '''
        font = ('Helvetica', 12, 'normal')
        frame = TesterFrame(master, font, testMessages)
        frame.pack()

    def on_closing(self):
        ''' Callback for close button '''
        reactor.stop()

#---------------------------------------------------------------------------#
# Main handle function
#---------------------------------------------------------------------------#
# This is called when the application is run from a console
# We simply start the gui and start the twisted event loop
#---------------------------------------------------------------------------#
def main():
    '''
    Main control function
    This either launches the gui
    '''

    testMessage = TestMessages('TestMessages.ini')

    tester = TesterApplication(root,testMessage)
    root.title("SimHost Test Application")
    root.protocol("WM_DELETE_WINDOW", tester.on_closing)
    reactor.run()

#---------------------------------------------------------------------------#
# Library/Console Test
#---------------------------------------------------------------------------#
# If this is called from console, we start main
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    main()