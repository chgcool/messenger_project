from psycopg2 import *

#вот тут я подключаюсь, все работает, руками не трогать
try:
    connection_string = "dbname = 'messenger' user = 'svyatoslav' host = 'localhost' password = 'Genetika1'" 
    connection = connect(connection_string)
    database = connection.cursor()
except:
    print("Unable to connect")

#Вопрос 1. Имеет ли смысл разбивать на отдельные классы? Файлы? Если да, то как?
#Вопрос 2. Имеет ли смысл как-то синтаксически оптимизировать передачу sql - запросов?
#Вопрос 3. Все ли нормально с этими запромами? Commit там какой-то?


class user:
    user_id = -1
    current_conversation = -1

    #входим, очевидно
    def log_in(self):

        #просим ввести username
        print("username:", end=' ')
        username = str(input())

        #проверяем, есть ли такой пользователь в системе, если нет, выдаем ошибку
        database.execute('SELECT * FROM users WHERE user_name = %s', (username, ))
        rows = database.fetchall()
        if len(rows) == 0:
            print('wrong username')
            return

        #и пароль
        print("password:", end = ' ') 
        password = str(input())

        user_row = rows[0]  
        if user_row[3] == password:
            self.user_id = user_row[0]
            print("logged in")
        else:
            print("wrong password")
            return

        print('---log_in', self.user_id) #debug


    #выдает list строк, отвечающих чатам, в которых мы участвуем
    def available_conversations(self):
        database.execute("""SELECT * FROM ((SELECT conversation_id FROM user_conversation WHERE user_id = %s) a \
            LEFT JOIN conversations USING (conversation_id))""", (self.user_id, ))
        rows = database.fetchall()

        print('---available_conversations', rows) #debug
        return rows


    #просто заходим в чат, в котором мы уже состоим
    def join_conversation(self):
        print("enter desired conversation name:", end=' ')
        conv_name = str(input())
        database.execute('SELECT * FROM conversations WHERE conversation_name = %s', (conv_name, ))
        rows = database.fetchall()
        if len(rows) == 0:
            print("there is no such conversation")
            return

        conversation_row = rows[0]

        if conversation_row not in self.available_conversations():
            database.execute('INSERT INTO user_conversation VALUES (%s, %s)', (self.user_id, conversation_row[0]))
            connection.commit() 
        self.current_conversation = conversation_row[0]

        print('---open_conversation', self.current_conversation)  #debug


    #создание чата
    def create_conversation(self):
        print("enter conversation name:", end=' ')
        conv_name = str(input())
        #с помощью RETURNING узнаем id созданного чата
        database.execute('INSERT INTO conversations (conversation_name, creator_id) VALUES (%s, %s) RETURNING conversation_id', \
         (conv_name, self.user_id))
        connection.commit()
        new_conv_id = database.fetchall()[0][0]

        database.execute('INSERT INTO user_conversation VALUES (%s, %s)', (self.user_id, new_conv_id))
        connection.commit()
        print("created conversation id is", new_conv_id) #debug


    #отправка сообщения
    def send_message(self):
        print("enter message:", end=' ')
        message = str(input())
        #и вновь с помощью returning узнаем id отправленного сообщения
        database.execute("""INSERT INTO messages (content, sender_id) VALUES (%s, %s) RETURNING message_id""", (message, self.user_id))
        connection.commit()
        message_id = database.fetchall()[0][0]

        database.execute("""INSERT INTO conversation_message VALUES (%s, %s)""", (message_id, self.current_conversation))
        connection.commit()


    #просто вывести все сообщения, упорядоченные по времени отправления, вместе с отправителем. Пока так(
    def show_conversation(self):
        database.execute("""SELECT b.content, b.delivery_time, users.user_name from
            (SELECT *, sender_id as user_id from ((SELECT message_id FROM conversation_message WHERE conversation_id = 26) a
            JOIN messages USING (message_id))
            ORDER BY delivery_time) b
            LEFT JOIN users USING (user_id)""", (self.current_conversation, ))
        rows = database.fetchall()
        for row in rows:
            print(row)

    

print('---1 log in', '---2 join conversation', '---3 create conversation', '---4 send message', '---5 show conversation', '---0 exit', sep='\n')
slavic = user()

print('\n---command:')
n = int(input())
while (n):
    if n == 1:
        slavic.log_in()
    if n == 2:
        slavic.join_conversation()
    if n == 3:
        slavic.create_conversation()
    if n == 4:
        slavic.send_message()
    if n == 5:
        slavic.show_conversation()

    print('\n---command:')
    n = int(input())
      
