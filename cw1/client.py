import socket
import os
from os.path import join, isfile, getsize
import multiprocessing
import threading
import struct
import time
import json
import hashlib


#Traversal folder
def traverse(dir_path):
    file_list = []
    file_folder_list = os.listdir(dir_path)
    for file_folder_name in file_folder_list:
        if isfile(join(dir_path, file_folder_name)):
            file_list.append(join(dir_path, file_folder_name))
        else:
            file_list.extend(traverse(join(dir_path, file_folder_name)))
    return file_list


def deal_file(serverName,severport):
    connect = False
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            if not connect:
                client_socket.connect((serverName, severport))
                print('file connect ok ------------------------')
                connect = True
                if connect:
                    try:
                        # get header
                        server_header_len_bytes = client_socket.recv(4)
                        server_header_int = struct.unpack('i', server_header_len_bytes)[0]
                        server_header_bytes = client_socket.recv(server_header_int).decode()
                        dic = json.loads(server_header_bytes)

                        # Total file size
                        Total_file_size = dic['file_size']
                        # Determine if there is a file that was last interrupted
                        if os.path.exists(dic['file_name'] + '.template_file'):
                            # The size of this file received
                            recv_size = getsize(dic['file_name'] + '.template_file')
                        else:
                            recv_size = 0
                        # Calculate how many blocks have been received
                        recv_block_num = int(recv_size // dic['buffer_size'])
                        print(recv_block_num)
                        # Send to the server how many packets have been received
                        b_str_block_num = str(recv_block_num).encode()
                        pak_recv = struct.pack('i', len(b_str_block_num))
                        client_socket.send(pak_recv)
                        client_socket.send(b_str_block_num)
                        position = recv_block_num * dic['buffer_size']

                        # receive files
                        with open(dic['file_name'] + '.template_file', 'ab') as f:
                            f.seek(position)
                            while True:
                                # receives a buffer_size block
                                content = client_socket.recv(dic['buffer_size'])
                                if content:
                                    # Writes the received block to the file
                                    f.write(content)
                                    # Show file transfer progress
                                    new_size = getsize(dic['file_name'] + '.template_file')
                                    plan_line = float(new_size * 100 / Total_file_size)
                                    print('download: %.2f %%' % plan_line)
                                else:
                                    break
                        if getsize(dic['file_name']+'.template_file') == Total_file_size:
                            print(1)
                            if os.path.exists(dic['file_name']):
                                os.remove(dic['file_name'])
                            os.rename(dic['file_name'] + '.template_file', dic['file_name'])
                            print(dic['file_name'], ' download succ')
                        else:
                            os.remove(dic['file_name'] + '.template_file')
                            print(dic['file_name'], ' download fail')

                        client_socket.close()
                        break
                    except Exception as A:
                        print(A.with_traceback())

        except Exception as E:
            connect = False
            client_socket.close()
# share folders
def mkdir(path):
    path=path.strip()
    path=path.rstrip("/")
    # Determine if the path exists
    isExists=os.path.exists(path)
    # Create a directory if none exists
    if not isExists:
        os.mkdir(path)
        return True
    # if it exists, it is not created
    else:
        return False

def main_B(serverName, folder_name):
    tcp = 22000
    serverport= 23000
    while True:
        connect = False
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if not connect:
            # Connect to server
                client_socket.connect((serverName,tcp))
                connect = True
                print('client start =')
                # Traverse the folder and send the list
                file_list = traverse(folder_name)
                header_str = json.dumps(file_list)
                client_socket.send(header_str.encode())

                # List of missing files
                diff_list_rec = client_socket.recv(4)
                list_len = struct.unpack('i', diff_list_rec)[0]
                str_list = client_socket.recv(list_len).decode()
                diff_list = json.loads(str_list)
                # path of folder
                for file_name in diff_list:
                    u1,u2=os.path.split(file_name)
                    mkdir(u1)
                # Charge times
                recv_time = len(diff_list)

                for a in range(recv_time):
                    p1 = threading.Thread(target=deal_file, args=(serverName,serverport))
                    p1.start()
                    p1.join()

        except Exception as A:
            print(A)
            pass


def main_B(serverName, folder_name):
    tcp = 22000
    serverport= 23000
    while True:
        connect = False
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if not connect:
            # Connect to server
                client_socket.connect((serverName,tcp))
                connect = True
                print('client start =')
                # Traverse the folder and send the list
                file_list = traverse(folder_name)
                header_str = json.dumps(file_list)
                client_socket.send(header_str.encode())

                # List of missing files
                diff_list_rec = client_socket.recv(4)
                list_len = struct.unpack('i', diff_list_rec)[0]
                str_list = client_socket.recv(list_len).decode()
                diff_list = json.loads(str_list)
                # path of folder
                for file_name in diff_list:
                    u1,u2=os.path.split(file_name)
                    mkdir(u1)
                # Charge times
                recv_time = len(diff_list)

                for a in range(recv_time):
                    p1 = threading.Thread(target=deal_file, args=(serverName,serverport))
                    p1.start()
                    p1.join()
        except Exception as A:
            A
            pass






if __name__ == '__main__':
    main_B('','share')
