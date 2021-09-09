import socket
import struct
import os
import multiprocessing
from os.path import join, isfile, getmtime, getsize
import json
import time
import threading
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


def connect_client(tcp_server_socket, file):
    buffer_size = 1024*1024
    server_socket, client_addr = tcp_server_socket.accept()
    print(client_addr,'start trans file:', file)
    file_size = getsize(file)
    block_num = int(file_size//buffer_size) + 1
    header_dic = {'file_name':file,'file_size':file_size,'buffer_size':buffer_size,'block_num':block_num}
    # header
    dic_file = json.dumps(header_dic).encode()
    header_len_bytes = struct.pack('i', len(dic_file))
    server_socket.send(header_len_bytes)
    server_socket.send(dic_file)

    # Receive received packages
    num_len_rec = server_socket.recv(4)
    str_num_len = struct.unpack('i', num_len_rec)[0]
    str_num = server_socket.recv(str_num_len).decode()
    recv_block_num = int(str_num)


    # Start sending where never sent before
    with open(file, 'rb') as f:
        # Where it has been sent
        new_position = recv_block_num * buffer_size
        print(new_position)
        f.seek(new_position)
        while True:
            content = f.read(buffer_size)
            if content:
                server_socket.send(content)
            else:
                break
    print("finish transfer")
    server_socket.close()







def server_main_1(folder_name):
    # Create socket, A,B
    server_socket_A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_B = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_A.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server_socket_B.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)


    # Binding information
    server_socket_A.bind(('', 22000))
    server_socket_B.bind(('', 23000))
    # Set to listen state
    server_socket_A.listen(128)
    server_socket_B.listen(128)
    while True:
        # Wait for a new client to connect
        print('Ready=')
        server_socket, client_addr = server_socket_A.accept()
        print(client_addr, '----already connect')
        # Receive file list
        file_list_json_str = server_socket.recv(20480).decode()
        file_list = json.loads(file_list_json_str)
        # List of local files
        local_file_list = traverse(folder_name)

        # Missing file list
        diff_list = list(set(local_file_list).difference(set(file_list)))
        for file_name in diff_list:
            if file_name.endswith('template_file'):
                diff_list.remove(file_name)

        diff_list_json_byte = json.dumps(diff_list).encode()
        diff_list_json_pak = struct.pack('i',len(diff_list_json_byte))

        server_socket.send(diff_list_json_pak)
        server_socket.send(diff_list_json_byte)
        print(diff_list)

        for file in diff_list:
            # Client sends file
            t_file = multiprocessing.Process(target=connect_client,
                                          args=(server_socket_B, file))
            t_file.start()
            t_file.join()


def server_main_1(folder_name):
    # Create socket, A,B
    server_socket_A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_B = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_A.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server_socket_B.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)


    # Binding information
    server_socket_A.bind(('', 22000))
    server_socket_B.bind(('', 23000))
    # Set to listen state
    server_socket_A.listen(128)
    server_socket_B.listen(128)
    while True:
        # Wait for a new client to connect
        print('Ready=')
        server_socket, client_addr = server_socket_A.accept()
        print(client_addr, '----already connect')
        # Receive file list
        file_list_json_str = server_socket.recv(20480).decode()
        file_list = json.loads(file_list_json_str)
        # List of local files
        local_file_list = traverse(folder_name)

        # Missing file list
        diff_list = list(set(local_file_list).difference(set(file_list)))
        for file_name in diff_list:
            if file_name.endswith('template_file'):
                 diff_list.remove(file_name)

        diff_list_json_byte = json.dumps(diff_list).encode()
        diff_list_json_pak = struct.pack('i',len(diff_list_json_byte))

        server_socket.send(diff_list_json_pak)
        server_socket.send(diff_list_json_byte)
        print(diff_list)

        for file in diff_list:
            # Client sends file
            t_file = multiprocessing.Process(target=connect_client,
                                          args=(server_socket_B, file))
            t_file.start()
            t_file.join()



if __name__ == '__main__':
     server_main_1('','share')
