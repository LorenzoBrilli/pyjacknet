#!/usr/bin/env python3

"""

    pyjacknet client

"""

import sys
import signal
import threading
import _thread
import numpy
import socket

from time import sleep
from shared.pyjacknet import JackHandler
import argparse
import ipaddress
from queue import Queue
import config
from constants import *

# ----- Global Variables
queue = Queue() #queue variable
opusEncoder = None #opus encoder, set only if needed
jackClient = None #jack client using jack handler
opusQueue = b'' #opus queue to store byte to encode
opusWindowSize = 0 #byte needed for opus window


# ----- Socket Handler
def socketHandler():
    while True:
        try:
            # get configuration
            host = config.ip
            port = config.port
            # create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            # try to connect
            try:
                s.connect((host, port))
                print("connected")
            except Exception as e:
                # if cannot connect wait and retry
                print("cannot connect")
                sleep(5)
                continue
            while True:
                try:
                    consumeQueue(s,opusEncoder)
                except Exception as e:
                    print("error while sending data")
                    print(e)
                    break
        except Exception as e:
            print("socket error")
            sleep(1)

def consumeQueue(s,opusEncoder):
    global opusQueue
    #check if anything in queue
    if (queue.qsize()>0):
        #get data
        data = queue.get()
        # ----- case no compression (32bit float)
        if (config.compression == PJN_COMPRESSION_32):
            # get bytes of data
            data = data.tobytes()
            #prepare packet_header
            #32bit integer for the length
            header = b''
            #header = header + numpy.int32(len(data)+4).tobytes()
            data = header + data
            #send data
            s.send(data)
        # ----- case 16 bit integer compression (16bit integer)
        elif (config.compression == PJN_COMPRESSION_16):
            # get bytes of data and convert it to int16
            data = (data*32767.0).astype(numpy.int16,copy=False).tobytes()
            #prepare packet_header (32bit integer for length)
            header = b''
            #header = header + numpy.int32(len(data)+4).tobytes()
            data = header + data
            #send data
            s.send(data)
        # ----- case opus encoding
        else:
            #convert to int16
            data = (data*32767.0).astype(numpy.int16,copy=False)
            #rearrange and transpose if stereo
            #we have all the left and then all the right and we want left,right intervealed
            if (config.channels == PJN_CHANNELS_STEREO):
                data = data.reshape(2,int(data.shape[0]/2)).transpose()
            #add data to opus queue
            opusQueue += data.tobytes()
            #process opus queue if enough data is present
            while (len(opusQueue)>=opusWindowSize):
                e_data = opusEncoder.encode(opusQueue[:opusWindowSize])
                header = numpy.int16(len(e_data)).tobytes()
                e_data = header + e_data
                opusQueue = opusQueue[opusWindowSize:]
                #print(e_data)
                #send data
                s.send(e_data)
            
            


# ----- JACK process callback
def process(frames):
    i1 = jackClient.getInPorts()[0]
    if (config.channels == PJN_CHANNELS_STEREO):
        i2 = jackClient.getInPorts()[1]
        data = numpy.concatenate((i1.get_array(),i2.get_array()))
    else:
        data = i1.get_array()
    try:
        queue.put(data)
    except Exception:
        print("cannot send data")

# ----- Opus Encoder Init
def initOpusEncoder():
    #create encoder
    opusEncoder = OpusEncoder()
    #set application
    opusEncoder.set_application("audio")
    #set samplerate
    opusEncoder.set_sampling_frequency(jackClient.getSampleRate())
    #set channel number
    opusEncoder.set_channels(config.channels)
    #calculate sample needed for 20ms window
    opusWindow = 20 #ms
    opusWindowSize = jackClient.getSampleRate() / 1000 * opusWindow
    if (config.channels == PJN_CHANNELS_MONO):
        opusWindowSize = opusWindowSize * 2
    else:
        opusWindowSize = opusWindowSize * 4
    opusWindowSize = int(opusWindowSize)
    return (opusEncoder, opusWindowSize)



def client_main():

    # start jack client using JackHandler
    jackClient = JackHandler("pjn_client",None,config.channels,0)
    jackClient.setProcessCallback(process)

    # if opus requested, import module and init the encoder
    if (config.compression == PJN_COMPRESSION_OPUS):
        try:
            from pyogg import OpusEncoder
        except Exception:
            print("Error: cannot find opus encoder")
            exit()
        opusEncoder,opusWindowSize = initOpusEncoder()

    
    # start tcp client
    _thread.start_new_thread(socketHandler, ())

    # activate jack
    jackClient.activate()

    # set an event to stop things
    event = threading.Event()
    print('Press Ctrl+C to stop')
    try:
        event.wait()
    except KeyboardInterrupt:
        print('\nInterrupted by user')
    except Exception:
        print('\nError ... closing')

    # try to close jack (if it is not closed)
    try:
        jackClient.close()
    except Exception:
        pass


if __name__ == '__main__':
    print("this file shold not be executed directly")