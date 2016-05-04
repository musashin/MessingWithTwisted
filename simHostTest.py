__author__ = 'nulysse'

import os
import ConfigParser
from twisted.internet import protocol, reactor, defer
from Tkinter import *
from twisted.internet import tksupport
root = Tk()
tksupport.install(root)


_SimHostListenPort = 6007
_GUI_send_port = 7000
_received_message_directory = 'replies'


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
    """
    This class used Twisted for UDP send/receive
    """

    rcv_msg_index = 0

    def __init__(self, receivedMsgList):
        self.receivedMsgList = receivedMsgList

    def datagramReceived(self, data, (host, port)):
        fileName = os.path.join(_received_message_directory,'reply{!s}'.format(self.rcv_msg_index))
        self.receivedMsgList.insert(END, "Received Message {!s}: content stored in {!s}\n".format(self.rcv_msg_index, fileName))

        if not os.path.isdir(_received_message_directory):
            os.makedirs(_received_message_directory)

        with open(fileName, 'wb') as msgData:
                msgData.write(data)

        self.rcv_msg_index +=1

    def write(self, data, host, port):
        self.transport.write(data, (host, port))

    def reset_msg_count(self):
        self.rcv_msg_index = 0


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

        frame = Frame(self,  bg='green')
        frame.grid(row=0, column=0, sticky="w")

        self.availablemessagelistbox = Listbox(frame)
        self.availablemessagelistbox.config(width=50)
        self.availablemessagelistbox .grid(row=0, column=0, columnspan=2, padx=2,sticky=N+S+E+W)

        for request in testMessages.request_list:
            self.availablemessagelistbox.insert(END, request)

        self.selectedmessagelistbox = Listbox(frame)
        self.selectedmessagelistbox.config(width=50)
        self.selectedmessagelistbox .grid(row=0, column=2, padx=2,sticky=N+S+E+W)

        self.sendButton = Button(frame, text="send", command=self.send_clicked, font=font)
        self.sendButton .grid(row=1, column=0, padx=2)

        self.addButton = Button(frame, text="add", command=self.add_message_to_send, font=font)
        self.addButton .grid(row=1, column=1, padx=2)

        self.clear = Button(frame, text="clear", command=self.clear, font=font)
        self.clear .grid(row=1, column=2, padx=2)

        self.receivedMsg = Text(frame, height=20,)
        self.receivedMsg .grid(row=2, column=0, columnspan=3, padx=2,sticky=N+S+E+W)

        self.guiEmulator = RemoteDebuggerGUI(self.receivedMsg)
        reactor.listenUDP(_SimHostListenPort, self.guiEmulator)


    def clear(self):
        self.selectedmessagelistbox.delete(0,END)
        self.receivedMsg.delete("1.0",END)
        self.guiEmulator .reset_msg_count()

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
        font = ('Helvetica', 10, 'normal')
        frame = TesterFrame(master, font, testMessages)
        frame.pack(side="top", fill="both", expand=True)

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