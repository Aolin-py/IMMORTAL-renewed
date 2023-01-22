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

def is_all_chinese(string=str):
    '''
        判断是否全部为中文
    '''
    for word in string:
        if not '\u4e00' <= word <= '\u9fa5':
            return False
    return True

def connect_db():
    '''
        创建数据库连接，返回一个conn对象
    '''
    try:
        conn = psycopg2.connect(
                            host='47.102.127.65', port=5433, user='xiao_dream', password='20080826Wal',
                            database='db9c7f1ffbc6444987ab816b503f125953Immortal') #连接数据库
    except Exception as e:
        logging.error(e)
    else:
        return conn #返回连接对象
    return None

def close_db(conn=psycopg2.connect): 
    '''
        关闭数据库
        注：数据库需关闭才能提交修改内容
    '''
    conn.commit() #提交
    conn.close() #关闭

def TimeString(string=str):
    '''
        在文本前添加时间
    '''
    Timestring = "[{Time}] {String}".format(Time=time.strftime("%H:%M:%S", time.gmtime()), String=string)
    return Timestring

def TimeAddrString(string,addr):
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
    '''
        主函数
    '''
    t1 = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建socket对象

    print(TimeString("正在连接至SQL服务器......"))

    conn_select = psycopg2.connect(
        host='47.102.127.65', port=5433, user='xiao_dream', password='20080826Wal',
         database='db9c7f1ffbc6444987ab816b503f125953Immortal') # 连接数据库

    print(TimeString("SQL连接成功！"))

    print(TimeString("正在绑定至端口{IP}:{Port}".format(IP=addrIP, Port=addrPort)))

    addr = (addrIP, addrPort)

    s.bind(addr)  # 绑定地址和端口

    logging.info('UDP Server on %s:%s...', addr[0], addr[1])

    print("[%s] 绑定成功！" % time.strftime("%H:%M:%S", time.gmtime()))
    t2 = time.time()
    t3 =  t2 - t1

    print("[%s] 服务器启动成功！（%.3fs）地址：[%s]" % (time.strftime("%H:%M:%S", time.gmtime()), t3, addr))

    user = {}  # 存放字典{地址 : [账户, 游戏名]}
    accounts = []
    logining = {} # 记录登录状态{地址：[(密码,),名称]}
    registering = {} # 记录注册状态{地址：[初次密码,名称]}
    entering = [] #记录为创建角色状态的账号[账户]

    
    '''
        以上为定义
        以下为循环
    '''

    while True:
        try:
            data, addr = s.recvfrom(4096)  # 等待接收客户端消息存放在2个变量data和addr里
            
            if not addr in user and data.decode('utf-8') not in accounts:  # 如果addr不在user字典里则执行以下代码
                if addr in logining.keys(): # 该IP处于登录状态
                    '''
                        以下为登录模块
                    '''
                    if data.decode('utf-8') == logining[addr][0][0]: # 注：result返回的是一个元组，内容为(XXXX,)
                        s.sendto("002".encode('utf-8'), addr) #发送登陆成功状态码
                        user[addr] = [logining[addr][1],''] #将该账户加入到在线列表
                        accounts += logining[addr][1]
                        del logining[addr] #将该用户从登陆状态中去除
                        print(TimeAddrString("{Y}<{Account}>加入了游戏{N}".format(Account=user[addr][0], Y=Y, N=N), addr))

                        conn_write = connect_db()
                        command = "UPDATE users SET login_time=CURRENT_TIMESTAMP(0) WHERE account='{Account}'".format(Account=data.decode('utf-8')) #更新登陆时间
                        with conn_write.cursor() as cursor:
                            cursor.execute(command)
                            close_db(conn_write) #提交登陆时间并关闭连接
                        '''
                            下面为角色登入/创建模块
                        '''
                        command = "SELECT name FROM attribute WHERE account='{Account}'".format(Account=user[addr][0]) #提取账户游戏角色
                        with conn_select.cursor() as cursor:
                            cursor.execute(command)
                            result = cursor.fetchone() #角色名称
                        if result:
                            s.sendto("008{Name}".format(Name=result[0]).encode('utf-8'), addr) #检测到账户有角色，进入游戏
                            user[addr][1] = result[0]
                            for address in user:
                                s.sendto("$L{Name}".format(Name=user[addr][1]).encode(), address) 
                        else:
                            s.sendto("006".encode('utf-8'), addr) #检测到没有角色，创建一个
                            entering.append(user[addr][0])
                        continue
                    else:
                        s.sendto("101".encode('utf-8'), addr) #密码错误
                    continue

                elif addr in registering: # 该IP处于注册状态
                    '''
                        以下为注册模块
                    '''
                    if registering[addr][0] == '': # 若无密码
                        registering[addr][0] = data.decode('utf-8') # 保存第一次输入的密码
                        s.sendto("004".encode("utf-8"), addr)

                    elif registering[addr][0] != '': # 若有密码
                        if registering[addr][0] == data.decode('utf-8'): # 比对前后密码是否一致
                            s.sendto("005".encode('utf-8'), addr)
                            conn_write = connect_db()
                            command = """INSERT INTO users (account,password)
                            VALUES ('{Account}','{Password}')""".format(
                                Account=registering[addr][1], Password=registering[addr][0]) # 向数据库中增添用户数据
                            with conn_write.cursor() as cursor:
                                cursor.execute(command)
                                close_db(conn_write) #提交注册信息
                            user[addr] = [registering[addr][1],'']
                            s.sendto("006".encode("utf-8"), addr) #注册必定没有角色，创建一个
                            entering.append(user[addr][0])
                            accounts += registering[addr][1]
                            
                            del registering[addr]

                        else: # 前后密码不一致
                            s.sendto("102".encode('utf-8'), addr) # 发送错误码
                            registering[addr][0] = '' # 将密码重置为空
                    continue

                else: # 新用户
                    '''
                        判断是否有账号
                    '''
                    command = "SELECT password FROM users WHERE account='{Account}'".format(Account=data.decode('utf-8'))
                    with conn_select.cursor() as cursor:
                        cursor.execute(command)
                        result = cursor.fetchone()

                        if result:  # 有密码，登录
                            s.sendto('001'.encode('utf-8'), addr)
                            logining[addr] = [result, data.decode('utf-8')]
                            # print(logining[addr][1][0])
                            print(TimeAddrString("<{Account}>正在尝试登陆...".format(Account=logining[addr][1]), addr))

                        elif not result: # 无密码，注册
                            s.sendto('003'.encode('utf-8'), addr)
                            registering[addr] = ['',data.decode('utf-8')] # {地址：[密码, 名称]}
                            print(TimeAddrString("<{Account}>正在尝试注册...".format(Account=registering[addr][1]), addr))
                    continue

            elif data.decode('utf-8') in user.values() and not addr in user.values():
                s.sendto("103".encode('utf-8'), addr) #重复登陆错误码
                continue
            
            if user[addr][0] in entering:
                '''
                    创建角色
                '''
                if is_all_chinese(data.decode("utf-8")):
                    user[addr][1] = data.decode("utf-8")
                    command = """INSERT INTO attribute (account,name)
                            VALUES ('{Account}','{Name}')""".format(Account = user[addr][0], Name = user[addr][1])
                    conn = connect_db()
                    with conn.cursor() as cursor:
                        cursor.execute(command)
                        close_db(conn)
                    s.sendto("007".encode("utf-8"), addr)
                    entering.remove(user[addr][0])
                    for address in user:
                        s.sendto("$L{Name}".format(Name=user[addr][1]).encode(), address)
                else:
                    s.sendto("104".encode('utf-8'), addr)

            if 'EXIT'.lower() in data.decode('utf-8'):#如果EXIT在发送的data里
                print(TimeAddrString("{Y}<{Account}>退出了游戏{N}".format(Account=user[addr][0], Y=Y, N=N), addr))
                name = user[addr][0]   #user字典addr键对应的值赋值给变量name
                user.pop(addr)      #删除user里的addr
                for address in user:    #从user取出address
                    s.sendto("$Q{Name}".format(Name=name).encode(), address)     #发送name和address到客户端

            else:
                print(TimeAddrString("<{Account}> {Message}".format(Account=user[addr][0],Message=data.decode('utf-8')), addr))
                if '#' in data.decode('utf-8')[:1]:  # 如果#在data里 
                    message = data.decode('utf-8')
                    for address in user:    #从user遍历出address
                        s.sendto(str(user[addr][0] + '##' + message).encode('utf-8'), address)     #发送data到address

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
    
    MainThread = threading.Thread(target=main, args=addrr, daemon=True, name='Main')
    InputThread = threading.Thread(target=main_input, args=(), name='Input')
    
    MainThread.start()
    time.sleep(0.2)
    InputThread.start()
