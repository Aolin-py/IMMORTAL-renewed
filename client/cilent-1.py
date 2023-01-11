#clinet.py
from color import *
import socket
import threading
import configparser
import os
from colorama import init
from pyfiglet import Figlet

init(autoreset=True)

def getConfig(section,key=None):
    '''
    获取[section]下[key]对应的值
    '''
    config = configparser.ConfigParser()
    dir = os.path.dirname(os.path.dirname(__file__))
    file_path = dir+'\\client\\config.ini'
    config.read(file_path,encoding='utf-8')
    if key!=None:
        return config.get(section,key)
    else:
        return config.items(section)

def writeConfig(section,key=None,value=None):
    '''
    将[section]下[key]的值定为[value]
    若只填写section，则创建[section]
    '''
    dir = os.path.dirname(os.path.dirname(__file__))
    os.chdir(dir + "\\client")
    config = configparser.ConfigParser()
    if key != None and value != None:
        config.add_section(section)
        for i in range(0,len(key)):
            config.set(section,str(key[i]),str(value[i]))
        f = open("config.ini","w+")
        config.write(f)
        f.close()


def recv(sock, addr):
    '''
    一个UDP连接在接收消息前必须要让系统知道所占端口
    也就是需要send一次，否则win下会报错
    '''
    sock.sendto(name.encode('utf-8'), addr) # 初始化连接发送名字
    print('已连接至服务器[%s:%s]' % (IP, port))
    while True:
        data = sock.recv(1024)
        message = data.decode('utf-8')
        if message == "001": #登录
            print("请输入{Y}密码{N}：".format(Y=Y, N=N))
            continue
        elif message == '002': #登陆成功
            print("{Y}登陆成功{N}".format(Y=Y,N=N))
            continue
        elif message == '003': #注册
            print("检测到您还没有账号，已跳转到{Y}注册{N}".format(Y=Y,N=N))
            print("请输入{Y}密码{N}：".format(Y=Y, N=N))
            continue
        elif message == "004": #注册-二次密码
            print("请{Y}再次输入密码{N}:".format(Y=Y, N=N))
            continue
        elif message == "005": #注册成功
            print("{Y}注册成功，已自动登录{N}".format(Y=Y, N=N))
            continue
        elif message == '101': #登录-密码错误
            print("{R}{BW}密码错误{N}".format(BW=BW,R=R,N=N))
            print("请重新输入{Y}密码{N}：".format(Y=Y,N=N))
            continue
        elif message == "102": #注册-前后密码不一致
            print("{R}前后密码不一致{N}".format(R=R,N=N))
            print("请重新输入{Y}密码{N}：".format(Y=Y,N=N))
            continue
        elif "##" in message: #他人说的话
            text = message.split("##",1) # 注：此处分割完成后列表为[名称,"",内容]，中间有空项
                                        # 只分割一次，所以对后面内容无影响
            # print(text)
            print("{Y}<{Name}>{N}{Text}".format(Y=Y,N=N,Name=text[0],Text=text[2]))
        elif message[0:1] == "$Q":
            Name = message.replace("$Q","",1)
            print("{Y}<{Name}>退出了游戏{N}".format(Y=Y,Name=Name, N=N))
        else:
            print(message)


def send(sock, addr):
    '''
        发送数据的方法
        参数：
            sock：定义一个实例化socket对象
            server：传递的服务器IP和端口
    '''
    while True:
        string = input('')
        message = string
        data = message.encode('utf-8')
        sock.sendto(data, addr)
        if string.lower() == 'EXIT'.lower():
            break

def main(IP, port):
    '''
        主函数执行方法，通过多线程来实现多个客户端之间的通信
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = (IP, port)
    tr = threading.Thread(target=recv, args=(s, server), daemon=True)
    ts = threading.Thread(target=send, args=(s, server))
    tr.start()
    ts.start()
    ts.join()
    s.close()

if __name__ == '__main__':
    logo = Figlet(font="lean", width=2000)
    print(Y + logo.renderText("Immortal") + N)
    while True:
        try:
            print(Y + "欢迎来到IMMORTAL！" + N)
            try:
                IP = getConfig("Internet","IP")
                port = int(getConfig("Internet","Port"))
            except configparser.NoSectionError:
                IP = input('请输入服务器{}IP{}：'.format(Y, N))
                port = int(input('请输入服务器{}端口{}：'.format(Y, N)))
                a = input("是否保存IP？{Y}是(Y)/否(N){N}".format(Y=Y, N=N))
                if a == "Y":
                    writeConfig("Internet",["IP","Port"],[IP,str(port)])
            print("====欢迎来到IMMORAL,退出请输入'EXIT(不分大小写)'====")
            name = input('请输入你的名称:')
            main(IP, port)
            break
        except TypeError or ValueError:
            print("输入错误，请正确输入端口号和IP")
        except ConnectionError:
            print(R,"连接中止！",N)
