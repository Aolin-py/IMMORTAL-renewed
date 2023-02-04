#server.py
import time
import socket
import logging #日志
import colorlog #日志彩色输出
import threading #多线程
import psycopg2 #数据库
import psycopg2.extras
import configparser #config读取
import os
#from pyfiglet import Figlet #LOGO打印
from color import * #颜色
from colorama import init #颜色初始化



# ↑日志器定义

class DataBaseConnection:
    def __init__(self, conn:psycopg2.connect) -> None:
        self.conn = conn

    def getAccountData(self) -> dict:
        '''
            返回的dict样式：{用户名:{"uuid":xxx, "password":xxx}}
        '''
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            command = "SELECT uuid,account,password FROM users"
            cursor.execute(command)
            result = cursor.fetchall()

        account = {}
        for i in range(0,len(result)):
            dict_result = dict(result[i])
            account[dict_result['account']] = {'uuid':dict_result['uuid'],'password':dict_result['password']}

        return account

    def getCharacterData(self) -> dict:
        '''
            返回的dict样式：{UUID:{角色ID:角色名, 角色ID:角色名,......}}
        '''
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            command = "SELECT UUID,character_id,character_name FROM character"
            cursor.execute(command)
            result = cursor.fetchall()

        character = {}
        for i in range(0,len(result)):
            dict_result = dict(result[i])
            if dict_result['uuid'] not in character:
                character[dict_result['uuid']] = {dict_result['character_id']:dict_result['character_name']}
                continue
            character[dict_result['uuid']][dict_result['character_id']] = dict_result['character_name']

        return character

    def getCharacterAttribute(self) -> dict:
        '''
            返回的dict样式：{(UUID,角色ID):{'hp':xxx,'hp_max':xxx,...}}
        '''
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            command = "SELECT * FROM attribute"
            cursor.execute(command)
            result = cursor.fetchall()
        
        attribute = {}
        for i in range(0,len(result)):
            dict_result = dict(result[i])
            attribute[(dict_result['uuid'],dict_result['character_id'])] = {
            'hp_max':dict_result['hp_max'],   'hp':dict_result['hp'], 
            'atk':dict_result['atk'],         'def':dict_result['def'], 
            'crit':dict_result['crit'],       'crit_damage':dict_result['crit_damage'],
            'dex':dict_result['dex'],         'pot':dict_result['pot'], 
            'lv':dict_result['lv'],           'exp':dict_result['exp'], 
            'exp_max':dict_result['exp_max'], 'coin':dict_result['coin']
            }

        return attribute

def IsAllChinese(string=str) -> bool:
    '''
        判断是否全部为中文
    '''
    for word in string:
        if not '\u4e00' <= word <= '\u9fa5':
            return False
    return True

def connectDB() -> psycopg2.connect:
    '''
        创建数据库连接，返回一个psycopg2.connect对象
    '''
    try:
        conn = psycopg2.connect(
            host='47.102.127.65', port=5433, 
            user='xiao_dream', password='20080826Wal',
            database='db9c7f1ffbc6444987ab816b503f125953Immortal') #连接数据库
    except Exception:
        logger.error("数据库连接失败！")
    else:
        return conn #返回连接对象
    return None

def closeDB(conn): 
    '''
        关闭数据库
        注：数据库需关闭才能提交修改内容
    '''
    conn.commit() #提交
    conn.close() #关闭

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

def getOnlineAccounts(user:dict) -> list:
    '''
        获取在线账户名
    '''
    user_list = user.values()
    online_accounts = []
    for i in range(0,len(user_list)):
        online_accounts.append(user_list[i]["account"])
    return online_accounts

def MainIn():
    '''
        主输入函数
    '''

    while True:   
        command = input("")
        if command.lower() == "exit".lower():
            if accountsDataNew:
                conn = connectDB()
                for account in accountsDataNew:
                    with conn.cursor() as cursor:
                        command = """INSERT INTO users (uuid,account,password) 
                        VALUES ({UUID},'{Account}','{Password}')""".format(
                            UUID=accountsDataNew[account]["uuid"],
                            Account=account,
                            Password=accountsDataNew[account]["password"])
                        cursor.execute(command)
                closeDB(conn)
            if charactersDataNew:
                conn = connectDB()
                for UUID in charactersDataNew:
                    with conn.cursor() as cursor:
                        command = """INSERT INTO character (uuid,character_id,character_name)
                        VALUES ({UUID},'{CharacterID}','{CharacterName}')""".format(
                            UUID=UUID,
                            CharacterID=list(charactersDataNew[UUID].keys())[0],
                            CharacterName=list(charactersDataNew[UUID].values())[0])
                        cursor.execute(command)
                closeDB(conn)
            exit()

        elif command.lower() == "online":
            logger.info("当前在线人员有：")
            user_values = list(user.values())
            for i in range(0,len(user_values)):
                print("- " + user_values[i]["account"])
        else:
            pass

def MainOut(sock):
    '''
        主输出函数
    '''
    
    global user, charactersAttributes, charactersData, accountsData

    while True:
        data, addr = sock.recvfrom(4096)  # 等待接收客户端消息存放在2个变量data和addr里
        message = data.decode('utf-8')
        # t1 = time.time()
        if not addr in user:  # 如果addr不在user字典里则执行以下代码
            '''
                判断是否有账号
            '''
            if message not in accountsData:  # 无账号，注册                    
                user[addr] = {
                    "account":message, 
                    "status":"reg"
                    }
                logger.info("<{Account}>正在尝试注册...".format(Account=message))    
                sock.sendto('003'.encode('utf-8'), addr)       
                continue
            else:                   
                user[addr] = {
                    "account":message, 
                    "status":"login", 
                    "password":accountsData[message]["password"], 
                    "uuid":accountsData[message]["uuid"]
                    }
                logger.info("{Y}<{Account}>正在尝试登陆...{N}".format(Account=message, Y=Y, N=N))
                sock.sendto('001'.encode('utf-8'), addr)
                continue
                
        elif user[addr]["status"] == "login": # 该IP处于登录状态
            '''
                以下为登录模块
            '''
            uuid = user[addr]["uuid"]
            if message != user[addr]["password"]: # 密码错误
                sock.sendto("101".encode('utf-8'), addr)
                continue
            else:
                conn_write = connectDB()
                command = "UPDATE users SET login_time=CURRENT_TIMESTAMP(0) WHERE account='{Account}'".format(Account=message) #更新登陆时间
                with conn_write.cursor() as cursor:
                    cursor.execute(command)
                    closeDB(conn_write) #提交登陆时间并关闭连接
                sock.sendto("002".encode('utf-8'), addr) #发送登陆成功状态码
            if not uuid in charactersData:
                user[addr]["status"] = "createCharacter"
                sock.sendto("006".encode('utf-8'), addr) #检测到没有角色，创建一个
                continue               
            #检测到账户有角色，选择角色
            else:
                user[addr]["status"] = "choseCharacter"
                sock.sendto(
                    "008{id};{characterName}".format(
                    id=list(charactersData[uuid].keys()), 
                    characterName=list(charactersData[uuid].values())).encode('utf-8'), 
                    addr)
                continue

        elif user[addr]["status"] == "reg": # 该IP处于注册状态
            '''
                以下为注册模块
            '''
            if "firstPassword" in user[addr] and user[addr]["firstPassword"] != message: # 若有密码且前后密码不一致
                del user[addr]["firstPassword"] # 将密码重置为空
                sock.sendto("102".encode('utf-8'), addr) # 发送错误码
                continue
            elif "firstPassword" in user[addr] and user[addr]["firstPassword"] == message: #前后密码一致，注册成功
                sock.sendto("005".encode('utf-8'), addr)
                user[addr]["password"] = user[addr]["firstPassword"]
                del user[addr]["firstPassword"]
                conn_write = connectDB()
                with conn_write.cursor() as cursor:
                    command = "SELECT nextval('uuid_seq')"
                    cursor.execute(command)
                    UUID = cursor.fetchone()[0]
                    user[addr]["uuid"] = UUID
                    accountsDataNew[user[addr]["account"]] = {"uuid":UUID, "password":user[addr]["password"]}
                closeDB(conn_write)               
                
                user[addr]["status"] = "createCharacter"
                charactersDataNew[user[addr]["uuid"]] = {}
                sock.sendto("006".encode("utf-8"), addr) #注册必定没有角色，创建一个
                continue
            else:
                user[addr]["firstPassword"] = message # 保存第一次输入的密码
                sock.sendto("004".encode("utf-8"), addr)               
                continue

        elif not addr in user and message in getOnlineAccounts(user):
            sock.sendto("103".encode('utf-8'), addr) #重复登陆错误码
            continue
        
        elif user[addr]["status"] == "createCharacter":
            '''
                创建角色
            '''
            uuid = user[addr]["uuid"]
            if not IsAllChinese(message): #若不全是中文
                sock.sendto("104".encode('utf-8'), addr)
                continue
            else:                 
                user[addr]["status"] = "online"
                try:
                    numberOfCharacters = len(charactersData[uuid])
                except KeyError:
                    numberOfCharacters = 0
                charactersDataNew[uuid][numberOfCharacters + 1] = message
                user[addr]["characterName"] = message
                user[addr]["characterID"] = numberOfCharacters + 1
                for address in user:
                    sock.sendto("$L{Name}".format(Name=message).encode(), address)
                logger.info("{Y}<{Account}>创建了{Character}角色并进入游戏...".format(
                    Account = user[addr]["account"], 
                    Character = user[addr]["characterName"], Y=Y, N=N))
                sock.sendto("007".encode("utf-8"), addr)
                continue

        elif user[addr]["status"] == "choseCharacter":
            '''
                选择角色
            '''
            uuid = user[addr]["uuid"]
            id_max = len(charactersData[uuid])
            try:
                if int(message) > id_max: #输入ID超出范围
                    sock.sendto("105".encode("utf-8"), addr)
                    continue
                elif message == "new":
                    user[addr]["status"] = "createCharacter"
                    sock.sendto("006".encode("utf-8"), addr)
                    continue
                else:
                    user[addr]["status"] = "online"
                    user[addr]["characterName"] = charactersData[uuid][int(message)]
                    user[addr]["characterId"] = int(message)
                    logger.info("{Y}<{Account}>以{Character}角色进入了游戏...".format(
                        Account = user[addr]["account"], 
                        Character = user[addr]["characterName"], Y=Y, N=N))
                    sock.sendto("009{Name}".format(Name=user[addr]["characterName"]).encode("utf-8"), addr)
                    continue
            except:
                continue

        elif '#' in data.decode('utf-8')[:1]:
            logger.info("<{Account}> {Message}".format(Account=user[addr]["account"],Message=message))
            for address in user:    #从user遍历出address
                try:
                    sock.sendto(str(user[addr]["characterName"] + '##' + message).encode('utf-8'), address)     #发送data到address
                except ConnectionResetError:
                    exit_account = user[address]["account"]
                    logger.warning("{Y}<{Account}>意外退出了游戏{N}".format(Account=exit_account))
                    user.pop(address)
                    for address in user:    #从user取出address
                        sock.sendto("$Q{Name}".format(Name=exit_account).encode(), address)
        if 'EXIT'.lower() in message:#如果EXIT在发送的data里
            logger.info("{Y}<{Account}>退出了游戏{N}".format(Account=user[addr]["account"], Y=Y, N=N))
            name = user[addr]["account"]
            for address in user:    #从user取出address
                sock.sendto("$Q{Name}".format(Name=name).encode(), address)     #发送name和address到客户端
            sock.sendto("exit".encode('utf-8'), addr)
            del user[addr]

        else:
            logger.info("<{Account}> {Message}".format(Account=user[addr]["account"],Message=message))

    

if __name__ == '__main__':
    logger = logging.getLogger("logger")

    console_handler = logging.StreamHandler()

    logger.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.DEBUG)

    log_colors_config = {
        'DEBUG': 'green',  # cyan white
        'INFO': 'white',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

    console_formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s][%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        log_colors=log_colors_config)

    console_handler.setFormatter(console_formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    console_handler.close()
    init(autoreset=True)
    #logo = Figlet(font="lean", width=1000)
    #print(Y + logo.renderText("Immortal") + N)
    
    try:
        addrIP = getConfig("Internet", "IP")
        addrPort = getConfig("Internet", "Port")
        addrr = (addrIP, int(addrPort))
        logger.info("已读取配置文件")
    except configparser.NoSectionError:
        logger.info('请输入服务器IP:')
        addrIP = input('>')
        logger.info('请输入服务器端口:')
        addrPort = int(input('>'))
        addrr = (addrIP, addrPort)
        a = input("是否保存IP？{Y}是(Y)/否(N){N}".format(Y=Y, N=N))
        if a == "Y":
            writeConfig("Internet")
            writeConfig("Internet",["IP","Port"],[addrIP,addrPort])
    
    t1 = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 创建socket对象

    logger.info("正在连接至SQL服务器...")

    conn_select = psycopg2.connect(
        host='47.102.127.65', port=5433, user='xiao_dream', password='20080826Wal',
         database='db9c7f1ffbc6444987ab816b503f125953Immortal') # 连接数据库

    logger.info("SQL连接成功！")
    logger.info("正在获取用户信息...")

    dbconn = DataBaseConnection(conn_select)

    accountsData = dbconn.getAccountData()
    charactersData = dbconn.getCharacterData()
    charactersAttributes = dbconn.getCharacterAttribute()
    charactersDataNew = {}
    accountsDataNew = {}
    user = {}  # 存放字典{地址 : {状态:"xxx", xx:xx, ...}}

    logger.info("获取成功！")

    logger.info("正在绑定至端口{IP}:{Port}".format(IP=addrIP, Port=addrPort))

    s.bind(addrr)  # 绑定地址和端口

    logger.info("绑定成功！")

    t2 = time.time()
    t3 =  t2 - t1
    
    MainInThread = threading.Thread(target=MainIn, args=(), name='MainIn')
    MainOutThread = threading.Thread(target=MainOut, args=(s,), name='MainOut')
    MainOutThread.setDaemon(True)
   
    MainInThread.start()
    MainOutThread.start()
    logger.info("服务器启动成功！（{:.2f}s）地址：[{IP}:{Port}]".format(t3, IP=addrr[0], Port=addrr[1]))
    MainInThread.join()
    s.close()
    conn_select.close()