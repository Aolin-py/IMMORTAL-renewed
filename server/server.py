#server.py
import time
import socket
import logging
import threading
import psycopg2
import configparser
import os
from pyfiglet import Figlet
from color import *
from colorama import init


def TimeString(string):
    '''
    在文本前添加时间
    '''
    Timestring = "[{Time}] {String}".format(Time=time.strftime("%H:%M:%S", time.gmtime()), String=string)
    return Timestring

def TimeAddrString(string, addr):
    '''
    在文本前添加时间和IP
    '''
    TimeAddrstring = "[{Time}] [{IP}:{Port}] {String}".format(
        Time=time.strftime("%H:%M:%S", time.gmtime()), IP=addr[0], Port=addr[1], String=string)
    return TimeAddrstring

def getConfig(section,key=None):
    '''
    获取[section]下[key]对应的值
    '''
    config = configparser.ConfigParser()
    dir = os.path.dirname(os.path.dirname(__file__))
    file_path = dir+'\\server\\config.ini'
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
    os.chdir(dir + "\\server")
    config = configparser.ConfigParser()
    if key != None and value != None:
        config.add_section(section)
        for i in range(0,len(key)):
            config.set(section,str(key[i]),str(value[i]))
        f = open("config.ini","w+")
        config.write(f)
        f.close()

def main_input():
    '''
    控制台指令输入
    '''
    while True:   
        command = input("> ")
        if command.lower() == "exit".lower():
            exit()
        else:
            pass

def main(addrIP,addrPort):
    t1 = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建socket对象

    print(TimeString("正在连接至SQL服务器......"))

    sql_conn = psycopg2.connect(host='47.102.127.65', port=5433, user='xiao_dream', password='20080826Wal', database='db9c7f1ffbc6444987ab816b503f125953Immortal') # 连接数据库

    print(TimeString("SQL连接成功！"))

    print(TimeString("正在绑定至端口{IP}:{Port}".format(IP=addrIP, Port=addrPort)))

    addr = (addrIP, addrPort)

    s.bind(addr)  # 绑定地址和端口

    logging.info('UDP Server on %s:%s...', addr[0], addr[1])

    print("[%s] 绑定成功！" % time.strftime("%H:%M:%S", time.gmtime()))
    t2 = time.time()
    t3 =  int((t2 - t1))

    print("[%s] 服务器启动成功！（%ss）地址：[%s]" % (time.strftime("%H:%M:%S", time.gmtime()), t3, addr))

    user = {}  # 存放字典{地址 : 名称}
    logining = {} # 记录登录状态{地址：[(密码,),名称]}
    registering = {} # 记录注册状态{地址：[初次密码,名称]}

    while True:
        try:
            data, addr = s.recvfrom(1024)  # 等待接收客户端消息存放在2个变量data和addr里
            
            if not addr in user:  # 如果addr不在user字典里则执行以下代码    
                if addr in logining.keys(): # 该IP处于登录状态
                    if data.decode('utf-8') == logining[addr][0][0]: # 注：result返回的是一个元组，内容为(password,)
                        s.sendto("002".encode('utf-8'), addr)
                        user[addr] = logining[addr][1]  
                        del logining[addr]
                        print(TimeAddrString("{Y}<{Name}>{N}加入了游戏".format(Name=user[addr], Y=Y, N=N), addr))
                        command = "UPDATE users SET login_time=NOW() WHERE user_name='{Name}'".format(Name=data.decode('utf-8'))
                        with sql_conn.cursor() as cursor:
                            cursor.execute(command)
                            sql_conn.commit()
                        continue
                    else:
                        s.sendto("101".encode('utf-8'), addr)
                    continue
                elif addr in registering: # 该IP处于注册状态
                    if registering[addr][0] == '': # 若无密码
                        registering[addr][0] = data.decode('utf-8') # 保存第一次输入的密码
                        s.sendto("004".encode("utf-8"), addr)
                    elif registering[addr][0] != '': # 若有密码
                        if registering[addr][0] == data.decode('utf-8'): # 比对前后密码是否一致
                            s.sendto("005".encode('utf-8'), addr)
                            command = """INSERT INTO users (user_name,passwords)
                            VALUES ('{Name}','{Password}')""".format(
                                Name=registering[addr][1], Password=registering[addr][0]) # 向数据库中增添用户数据
                            with sql_conn.cursor() as cursor:
                                cursor.execute(command)
                                sql_conn.commit()
                            user[addr] = registering[addr][1]
                            print(TimeAddrString("{Y}<{Name}>（新）加入了游戏{N}".format(Name=user[addr], Y=Y, N=N), addr))
                            del registering[addr]
                        else: # 前后密码不一致
                            s.sendto("102".encode('utf-8'), addr) # 发送错误码
                            registering[addr][0] = '' # 将密码重置为空
                    continue
                else: # 新用户
                    command = "SELECT passwords FROM users WHERE user_name='{Name}'".format(Name=data.decode('utf-8'))
                    with sql_conn.cursor() as cursor:
                        cursor.execute(command)
                        result = cursor.fetchone()
                        if result:  # 有密码，登录
                            s.sendto('001'.encode('utf-8'), addr)
                            logining[addr] = [result, data.decode('utf-8')]
                            # print(logining[addr][1][0])
                            print(TimeAddrString("<{Name}>正在尝试登陆...".format(Name=logining[addr][1]), addr))
                        elif not result: # 无密码，注册
                            s.sendto('003'.encode('utf-8'), addr)
                            registering[addr] = ['',data.decode('utf-8')] # {地址：[密码, 名称]}
                            print(TimeAddrString("<{Name}>正在尝试注册...".format(Name=registering[addr][1]), addr))
                    continue
            if 'EXIT'.lower() in data.decode('utf-8'):#如果EXIT在发送的data里
                print(TimeAddrString("{Y}<{Name}>退出了游戏{N}".format(Name=user[addr], Y=Y, N=N), addr))
                name = user[addr]   #user字典addr键对应的值赋值给变量name
                user.pop(addr)      #删除user里的addr
                for address in user:    #从user取出address
                    s.sendto("$Q{Name}".format(Name=name).encode(), address)     #发送name和address到客户端

            else:
                print(TimeAddrString("<{Name}> {Message}".format(Name=user[addr],Message=data.decode('utf-8')), addr))
                if '#' in data.decode('utf-8')[:1]:  # 如果#在data里 
                    message = data.decode('utf-8')
                    for address in user:    #从user遍历出address
                        s.sendto(str(user[addr] + '##' + message).encode('utf-8'), address)     #发送data到address


        except ConnectionResetError:
            pass


if __name__ == '__main__':
    print(TimeString("初始化颜色......"))
    init(autoreset=True)
    print(TimeString("初始化颜色成功！"))
    logo = Figlet(font="lean", width=1000)
    print(Y + logo.renderText("Immortal") + N)
    
    try:
        addrIP = getConfig("Internet", "IP")
        addrPort = getConfig("Internet", "Port")
        addrr = (addrIP, int(addrPort))
    except configparser.NoSectionError:
        addrIP = input(TimeString('请输入服务器IP:'))
        addrPort = int(input(TimeString('请输入服务器端口:')))
        addrr = (addrIP, addrPort)
        a = input("是否保存IP？{Y}是(Y)/否(N){N}".format(Y=Y, N=N))
        if a == "Y":
            writeConfig("Internet")
            writeConfig("Internet",["IP","Port"],[addrIP,addrPort])
    
    MainThread = threading.Thread(target=main, args=addrr, daemon=True)
    InputThread = threading.Thread(target=main_input, args=())
    
    MainThread.start()
    time.sleep(0.2)
    InputThread.start()
