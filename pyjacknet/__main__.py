#!/usr/bin/env python3

"""

    PyJackNet - Real Time Audio Streaming Utility Using Jack

"""

import argparse
import ipaddress
from constants import *
import config
import pyjacknet_client


# ------ parse arguments
def parse_arguments():
    # create parser
    parser = argparse.ArgumentParser()
    # add arguments
    parser.add_argument('mode', help='operating mode: client or server', choices=['client','server'])
    parser.add_argument('-i','--ip', help='ip', default='127.0.0.1')
    parser.add_argument('-p','--port', type=int, help='port', default='54345')
    parser.add_argument('-c','--channels', help='number of channels',choices=['1,2,mono,stereo'], default='stereo')
    parser.add_argument('-x','--compression', help='compression: 32bit floating point, 16bit integer or opus encoding',choices=['32','16','opus'], default='16')
    args = parser.parse_args()
    # create variables
    mode = args.mode
    ip = args.ip
    port = args.port
    channels = args.channels
    compression = args.compression
    # test validity  
    if (mode == 'server'):
        mode = PJN_MODE_SERVER
    else:
        mode = PJN_MODE_CLIENT
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

    if (compression == '32'):
        compression = PJN_COMPRESSION_32
    elif (compression == '16'):
        compression = PJN_COMPRESSION_16
    else:
        compression = PJN_COMPRESSION_OPUS

    config.mode = mode
    config.ip = ip
    config.port = port
    config.channels = channels
    config.compression = compression

    return True



if __name__ == '__main__':
    print("PyJackNet - audio streaming using jack\n")
    parse_arguments()
    if config.mode == PJN_MODE_CLIENT:
        pyjacknet_client.client_main()
    else:
        print("server mode not implemented yet")
