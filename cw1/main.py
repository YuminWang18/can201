import socket
import struct
import os
import multiprocessing
import time
import threading
import hashlib
import json
import client
import server
from os.path import join, isfile, getmtime, getsize
from client import main_B

from server import server_main_1

import argparse


def _argparse():
    parser = argparse.ArgumentParser(description="This is description!")
    parser.add_argument('--ip', type=str)
    return parser.parse_args()

# get ip address
def ip_address():
    parser = _argparse()
    two_ip_address = _argparse().ip.split(',')
    global ip_address1
    ip_address1 = two_ip_address[0]
    global ip_address2
    ip_address2 = two_ip_address[1]



if __name__ == '__main__':
    folder_name='share'
    ip_address()
    isExists = os.path.exists(folder_name)
    if not isExists:
        os.mkdir(folder_name)

    while True:
        p1 = multiprocessing.Process(target=server_main_1, args=(folder_name,))

        p2 = multiprocessing.Process(target=server_main_1, args=(folder_name,))


        p3 = multiprocessing.Process(target=main_B, args=(ip_address1,folder_name))
        p4 = multiprocessing.Process(target=main_B, args=(ip_address2, folder_name))
        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p3.join()
        p4.join()



