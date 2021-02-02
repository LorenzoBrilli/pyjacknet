#!/usr/bin/env python3

"""

    PyJackNet - Configuration module

"""

from constants import *

# Global Variables
mode = PJN_MODE_SERVER
ip = '127.0.0.1'
port = 54345
channels = PJN_CHANNELS_STEREO
compression = PJN_COMPRESSION_16

if __name__ == '__main__':
    print("this file shold not be executed directly")