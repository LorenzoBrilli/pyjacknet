#!/usr/bin/env python3

"""

    pyjacknet client

"""

import jack
from time import sleep
import threading
import _thread

# ----- JackHandler Class
# class used to handle jack
class JackHandler:

    client = None

    # init jack
    def __init__(self, clientname, servername=None, inports=2, outports=2):
        #create client
        self.client = jack.Client(clientname, servername=servername)
        #notify
        if self.client.status.server_started:
            print('JACK server started')
        if self.client.status.name_not_unique:
            print('unique name {0!r} assigned'.format(self.client.name))
        #register ports:
        for n in range(inports):
            self.client.inports.register('input_{0}'.format(n))
        for n in range(outports):
            self.client.outports.register('outport_{0}'.format(n))
        #set shutdown callback
        self.client.set_shutdown_callback(self.shutdownCallback)
    
    #set process callback
    #NB. do this prior to activation
    def setProcessCallback(self,callback):
        self.client.set_process_callback(callback)

    #shutdown callback
    def shutdownCallback(self,status,reason):
        print('JACK shutdown!')
        print('status:', status)
        print('reason:', reason)

    #activate jack
    def activate(self):
        # jack runs on a separate thread and use callback to communicate with pyjacknet
        self.client.activate()

    #close connection
    def close(self):
        self.client.deactivate()
        self.client.close()

    #connect outputs (if any) to playback (if any)
    #NB. do this after activating
    def connect_output(self):
        try:
            playback = self.client.get_ports(is_physical=True, is_input=True)
            if not playback:
                raise RuntimeError('No physical playback ports')

            for src, dest in zip(self.client.outports, playback):
                self.client.connect(src, dest)

            return True
        except:
            return False

    #get input ports
    def getInPorts(self):
        return self.client.inports

    #get output ports
    def getOutPorts(self):
        return self.client.outports

    #return an integer with samplerate
    def getSampleRate(self):
        return self.client.samplerate

if __name__ == '__main__':
    print("this file shold not be executed directly")