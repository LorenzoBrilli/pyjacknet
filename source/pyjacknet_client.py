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

# ----- Global Variables
config = () #config variable
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
            host = config[0]
            port = config[1]
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
        if (config[3] == 0):
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
        elif (config[3] == 1):
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
            if (config[2] == 2):
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
    if (config[2] == 2):
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
    opusEncoder.set_channels(config[2])
    #calculate sample needed for 20ms window
    opusWindow = 20 #ms
    opusWindowSize = jackClient.getSampleRate() / 1000 * opusWindow
    if (config[2] == 1):
        opusWindowSize = opusWindowSize * 2
    else:
        opusWindowSize = opusWindowSize * 4
    opusWindowSize = int(opusWindowSize)
    return (opusEncoder, opusWindowSize)


# ------ parse arguments
def parse_arguments():
    # create parser
    parser = argparse.ArgumentParser()
    # add arguments
    parser.add_argument('-i','--ip', help='ip of the server', default='127.0.0.1')
    parser.add_argument('-p','--port', type=int, help='port of the server', default='54345')
    parser.add_argument('-c','--channels', help='number of channels',choices=['1,2,mono,stereo'], default='stereo')
    parser.add_argument('-x','--compression', help='compression: 32bit floating point, 16bit integer or opus encoding',choices=['32','16','opus'], default='16')
    args = parser.parse_args()
    # create variables
    ip = args.ip
    port = args.port
    channels = args.channels
    compression = args.compression
    # test validity
    try:
        ipaddress.ip_address(ip)
    except:
        print("invalid ip")
        exit()
    if port > 65535:
        print("invalid port")
        exit()
    if (channels == '1' or channels == 'mono'):
        channels = 1
    else:
        channels = 2
    print("server at {}:{}".format(ip,port))
    print("channel number: {}".format(channels))
    print("compression is {}".format(compression))
    print("")
    if (compression == '32'):
        compression = 0
    elif (compression == '16'):
        compression = 1
    else:
        compression = 2

    return (ip,port,channels,compression)

if __name__ == '__main__':

    print("pyjacknet_client - audio streaming using jack\n")
    config = parse_arguments()


    # start jack client using JackHandler
    jackClient = JackHandler("pjn_client",None,config[2],0)
    jackClient.setProcessCallback(process)

    # if opus requested, import module and init the encoder
    if (config[3] == 2):
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