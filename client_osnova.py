from socket import *




while True:
    try:
        client_socket=socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 2221))#подключение к серверу
        print('введите messageID:')
        mes=input();
        soobshenie=str('connection;ClientID:127.0.0.1;messageID:'+mes+';')
        #connection;ClientID:127.0.0.1;messageID:12; - формат сообщения
        zaproc_podkluch=soobshenie.encode('utf-8')#отправка сообщения серверу ip и кодом сообщения
        
        client_socket.send(zaproc_podkluch)#отправка сообщения серверу
        if zaproc_podkluch.decode('utf-8')=='exit\n':#если клиент отправил запрос на отключение
            break
        data=client_socket.recv(1024).decode('utf-8') #получение ответа сервера
        print(data)
        #if data.partition('messageID:')[2].partition(';')[0].find(zaproc_podkluch.decode('utf-8').partition('messageID:')[2].partition(';')[0])==-1:
        #если сервер прислал ответ с ошибкой "-1"
        if int(data.partition('messageID:')[2].partition(';')[0])==-1:
            break
        #если код сообщения ответа сервера соответствует коду сообщения запроса клиента 
        if data.partition('messageID:')[2].partition(';')[0].find(zaproc_podkluch.decode('utf-8').partition('messageID:')[2].partition(';')[0])!=-1:
            ex=0
            for i in range(3):
                if ex==1:
                    break
                #authentication;Login:илья;password:2312;messageID:2;
                print('введите пароль:')
                pas=input();
                print('введите логин:')
                log=input();
                print('введите messageID:')
                mes=input();
                sborka=str('authentication;Login:'+log+';password:'+pas+';messageID:'+mes+';')
                otvet_login=sborka.encode('utf-8')#формирование сообщения с логином и паролем
                client_socket.send(otvet_login)#отправка сообщения серверу
                if otvet_login.decode('utf-8')=='exit':#если клиент хочет разорвать соединение
                    break
                data=client_socket.recv(1024).decode('utf-8') #получение ответа сервера 
                print(data)
                #если код запроса соответствует коду ответа 
                if data.partition('messageID:')[2].partition(';')[0]==otvet_login.decode('utf-8').partition('messageID:')[2].partition(';')[0]:
                    for i in range(3):
                        if ex==1:
                            break
                        #Save file;messageID:3;filename:file.txt;
                        print('введите полное название файла:')
                        fil=input();
                        print('введите messageID:')
                        mes=input();
                        sborka=str('Save file;messageID:'+mes+';filename:'+fil+';')
                        filename=sborka.encode('utf-8')
                        client_socket.send(filename)#отправка сообщения серверу
                        if filename.decode('utf-8')=='exit': #если клиент хочет выйти
                            ex=1
                        data=client_socket.recv(1024).decode('utf-8') #получение ответа сервера
                       # print(data)
                        if data=='1':# если сервер прислал 1, значит он готов к передаче файла 
                            client_socket.send('1'.encode('utf-8'))#отправка сообщения серверу чтобы отделить обычные сообщения от передачи файла
                            #формирование файла для записи информации полученной от сервера
                            f=open('file_client/'+str(filename.decode('utf-8').partition('filename:')[2].partition(';')[0]), 'wb+')
                            #получение файла
                            while True:
                                serv_data = client_socket.recv(1024)
                                #print(serv_data)
                                if not serv_data:
                                    f.close()
                                    ex=1

                                    break
                                
                                f.write(serv_data)
                               
                        elif data.partition('messageID:')[2].partition(';')[0]!='1':
                            print(data)
                            if i==2:
                                ex=1
                                break
                
        
        
        
        
        
    except KeyboardInterrupt:
        print('Ошибка. подключение разорвано')
    break
    
client_socket.close()