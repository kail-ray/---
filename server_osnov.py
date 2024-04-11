from socket import *
import os.path
import re
def poisk_ip(data): # функция проверки IP-адреса программы-клиенты. в случае отсутсвия адреса в списке север разрывает соединение с клиентом
    f=open('адреса.txt', 'r+', encoding='utf-8')
    ip=None
    a=list(f)
    for i in range(len(a)):
        if a[i].find(data)!=-1:
            ip=1
    if ip==None:
        ip=0
    return ip
    f.close()
def authentication(pas):#функция проверки логина и пароля в базе данных 
    f=open('пароли.txt', 'r+', encoding='utf-8')
    n=None
    a=list(f)
    for i in range(len(a)):
        if a[i]==pas+'\n':
            n=1
    if n==None:
        n=0
    return n
    f.close()
  
  
  
  
s = socket(AF_INET, SOCK_STREAM) #протокол IPv4, тип сокета может быть SOCK_STREAM (TCP)
s.bind(('127.0.0.1', 2221))# связывает сокет с локальными адресом
while True:
    try:
        try:
            s.listen()   # устанавливает серверный сокет в режим ожидания соединения
            client_socket, addres = s.accept() #принимает новое соединение на серверном сокете
            #первоначально проверяется ip затем логин и пароль.
            #аутентификация происходит только после нахождения совпадения ip с ip в базе данных 
            # аутентификация при неверном вводе происходит 3 раза, далее идёт разрыв соединения
            #
            #
            st=str(client_socket.recv(1024).decode('utf-8'))#получение от клиента его ip и кода сообщения
            if st=='exit\n':# если клиент хочет закрыть соединение
                client_socket.shutdown(SHUT_WR)#закрытие соединения с данным клиентом
                
            ip=str(addres[0])
            print(ip + ' прислал: ' + st)
            if ((st.find('connection')!=-1) and (st.find('ClientID:')!=-1) and (st.find('messageID:')!=-1)):
                ClientID=st.partition('ClientID:')[2].partition(';')[0]
                if (poisk_ip(ClientID))==0:
                    print('ip не найден')
                    client_socket.shutdown(SHUT_WR)
                if (poisk_ip(ClientID))==1:#если ip адрес присутствует в списке адресов сервера
                    messageID=st.partition('messageID:')[2].partition(';')[0]
                    print(str(ip+' подключился к серверу\n'))
                    otvet_s=str('\nconnection;ClientID:'+ip+';messageID:'+str(messageID)+';answer:вы подключились к серверу\nпришлите свой логин и пароль в формате соответствующем протоколу;\n').encode('utf-8')#написание и декодирование сообщения
                    client_socket.send(otvet_s)#отправка сообщения клиенту
                    
                    
                    for i in range(3):#проверка пароля 
                        pas=str(client_socket.recv(1024).decode('utf-8'))
                        if pas=='exit\n':# если клиент хочет закрыть соединение
                            print(666)
                            client_socket.shutdown(SHUT_WR)#закрытие соединения с данным клиентом
                            
                        if ((pas.find('authentication')!=-1) and (pas.find('Login:')!=-1) and (pas.find('password:')!=-1) and (pas.find('messageID:')!=-1)):
                            print(ip + ' прислал: ' + pas)
                            Login=pas.partition('Login:')[2].partition(';')[0]
                            password=pas.partition('password:')[2].partition(';')[0]
                            (authentication(str(Login)+' '+str(password)))
                            
                            if (authentication(str(Login)+' '+str(password)))==1:#проверка логина и пароля в бд сервера
                                messageID=pas.partition('messageID:')[2].partition(';')[0]
                                otvet_s=str('\nauthentication;messageID:'+str(messageID)+';answer:вы прошли аутентификацию. Пришлите имя файла;\n').encode('utf-8')#написание и декодирование сообщения
                                client_socket.send(otvet_s)#отправка сообщения клиенту
                                print(str(ip+' прошёл аутентификацию\n'))
                                
                                for i in range(3): 
                                    data = client_socket.recv(1024).decode('utf-8')# получение сообщения с именем файла
                                    print(ip + ' прислал: ' + data)
                                    if data=='exit\n':# если клиент хочет закрыть соединение
                                        client_socket.shutdown(SHUT_WR)#закрытие соединения с данным клиентом
                                    data=re.sub('\n','',data)# удаление переноса строки
                                    if ((data.find('Save file')!=-1) and (data.find('filename:')!=-1) and (st.find('messageID:')!=-1)):
                                   #============================================================================================================
                                        #передача файла если имя файла найдено среди существующих в бд сервера
                                        filename=data.partition('filename:')[2].partition(';')[0]
                                        if (os.path.exists('file_server/'+filename))==True: #
                                            otvet_s=str('1').encode('utf-8')#написание и декодирование сообщения
                                            client_socket.send(otvet_s)#отправка сообщения клиенту
                                            data = client_socket.recv(1024).decode('utf-8')# получение сообщени
                                            print(data)
                                            f = open('file_server/'+filename, 'rb')
                                            inf= ''
                                            while inf!= b'':
                                                inf=f.read(1024)
                                                client_socket.send(inf)
#+-=-=-=-=-=-==-=-=-=-=-=-=-
                                                
                                            client_socket.shutdown(SHUT_WR)
                                            break
                                        else:# выполняется если имя файла не найдено
                                            otvet_s=str('\nSave file;messageID:-1;answer:неправильное имя файла;\n').encode('utf-8')#написание и декодирование сообщения
                                            client_socket.send(otvet_s)#отправка сообщения клиенту
                                            if i==2:
                                                client_socket.shutdown(SHUT_WR)#закрытие соединения с данным клиентом после отправления ему ответ
                                    else:#выполняется если сообщение не соответствует протоколу
                                        otvet_s=str('\nSave file;messageID:-1;answer:неправильный формат ввода названия файла;\n').encode('utf-8')#написание и декодирование сообщения
                                        client_socket.send(otvet_s)#отправка сообщения клиенту
                                        if i==2:
                                            client_socket.shutdown(SHUT_WR)#закрытие соединения с данным клиентом после отправления ему ответ
                            else:#выполняется если неверные логин или пароль
                                otvet_s=str('\nauthentication;messageID:-1;answer:неправильный логин или пароль;\n').encode('utf-8')#написание и декодирование сообщения
                                client_socket.send(otvet_s)#отправка сообщения клиенту
                                if i==2:
                                    client_socket.shutdown(SHUT_WR)#закрытие соединения с данным клиентом после отправления ему ответа
                                
                            
                            
                        else:#если фоpмат сообщения не соответствует тому что в протоколе
                            otvet_s=str('\nauthentication;ClientID:'+ip+';messageID:-1;answer:неправильный формат сообщения;\n').encode('utf-8')#написание и декодирование сообщения
                            client_socket.send(otvet_s)#отправка сообщения клиенту
                            if i==2:
                                client_socket.shutdown(SHUT_WR)#закрытие соединения с данным клиентом после отправления ему ответа
                
                
                
            else:#если формат сообщения не соответствуют тем что в протоколе 
                otvet_s=str('\nconnection;ClientID:'+ip+';messageID:-1;answer:неправильный формат сообщения;\n').encode('utf-8')#написание и декодирование сообщения
                client_socket.send(otvet_s)#отправка сообщения клиенту
                client_socket.shutdown(SHUT_WR)
        except BrokenPipeError:
            print('ошибка, подключение разорвано')
    except IsADirectoryError:
        print('ошибка, подключение разорвано')
