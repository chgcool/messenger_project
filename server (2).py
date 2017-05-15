import socket
from psycopg2 import *
from threading import Thread
from sys import exit

#Класс для отправления и получения данных в формате STRING
class server:
	sock = None

	def __init__(self):
		self.sock = socket.socket()
		self.sock.bind(("localhost", 14900))
		self.sock.listen(10)


	def send(self, conn, data):
		conn.send(data.encode("utf-8"))


	def receive(self, conn):
		data = conn.recv(1024)
		return data.decode("utf-8")

	def __del__(self):
		self.sock.close()


#класс для связи с базой данных, на вход принимает команду, возвращает, в зависимости от
#команды, список кортежей или ничего
class database:

	db_connection = None
	cursor = None

	def __init__(self):
		con_str = "dbname = 'messenger' user = 'svyatoslav' host = 'localhost' password = 'Genetika1'"
		self.db_connection = connect(con_str)
		self.cursor = self.db_connection.cursor()

	#функция с возвратом, для выборок
	def fetch(self, command):
		self.cursor.execute(command[0], command[1])
		self.db_connection.commit()
		rows = self.cursor.fetchall() 
		return rows

	#без возврата, только для вставки, удаления и т.д.
	def execute(self, command):
		self.cursor.execute(command[0], command[1])
		self.db_connection.commit()


#создаем экземпляры классов
db = database()
server_ = server()

#здесь будут хранииться подключенные полбзователи
users = []


#класс подключенного пользователя, с данными о нем и функциями 
#регистрации, создания переписки, отправки сообщений и т.д.
class user:

	user_id = None
	user_name = None

	#вошел ли пользователь в свой акк?
	signed_in = 0

	#id текущей переписки
	current_conv = None

	#ссылка на соединение
	conn = None

	def __init__(self, conn):
		self.conn = conn


	def sign_in(self):
		#считываем имя и пароль
		username = server_.receive(self.conn)

		server_.send(self.conn, "smth")
		password = server_.receive(self.conn)

		#проверка на существование
		command = """SELECT * FROM users WHERE user_name = %s;""", (username, )
		rows = db.fetch(command)

		if len(rows) == 0:
			server_.send(self.conn, "there is no such username")
			return

		#проверка на повторный вход
		command = """SELECT * FROM logged_in WHERE user_name = %s;""", (username, )
		if len(db.fetch(command)) > 0:
			server_.send(self.conn, "such user has already logged in")
			return

		#проверка на корректность
		user_row = rows[0]
		if user_row[2] != password:
			server_.send(self.conn, "wrong password")
			return

		self.user_id = user_row[0]
		self.user_name = username
		self.signed_in = 1

		#поддтверждаем вход, добавив в соответствующую таблицу
		command = """INSERT INTO logged_in (user_id, user_name) VALUES (%s, %s);""", \
		(self.user_id, username)
		db.execute(command)

		server_.send(self.conn, "you've signed in")


	def create_conversation(self):
		conv_name = server_.receive(self.conn)

		#проверка на существование чата с таким именем
		command = """SELECT * FROM conversations WHERE (conversation_name = %s);""", (conv_name, )
		if len(db.fetch(command)) > 0:
			server_.send(self.conn, "wrong")
			return

		#добавляем созданный чат в таблицу
		command = """INSERT INTO conversations (conversation_name) 
		 			 VALUES (%s);""", (conv_name)
		db.execute(command)

		server_.send(self.conn, "true")


	def show_available(self):
		command = """SELECT conversation_name FROM conversations;""", (1, )
		rows = db.fetch(command)
		result = ""
		for row in rows:
			result += row[0] + "\n"
		server_.send(self.conn, result)

	#в этой функции мы входим в переписку и пвыводим все ранее отправленные сообщения
	def join_conversation(self):

		#считываем название переписки
		conv_name = server_.receive(self.conn)

		#проверяем существование
		command = """SELECT * FROM conversations WHERE conversation_name = %s""", (conv_name, )
		rows = db.fetch(command)
		if len(rows) == 0:
			server_.send(self.conn, "There is no such conversation")
			return 0

		server_.send(self.conn, "true")

		#поддтверждаем вход в чат добавлением в соотв. таблицу
		conversation_id = rows[0][0]
		command = """INSERT INTO user_conversation VALUES (%s, %s)""", (self.user_id, conversation_id)
		db.execute(command)


		self.current_conv = conversation_id

		#выводим все ранее нотправленные сообщения
		command = """SELECT user_name, content FROM 
			(SELECT sender_id AS user_id, delivery_time, content FROM 
			(SELECT * FROM conversation_message WHERE conversation_id = %s) a
			JOIN messages USING (message_id)) b
			JOIN users USING (user_id) ORDER BY b.delivery_time;""", (self.current_conv, )


		rows = db.fetch(command)
		s = "---"
		for row in rows:
			s += str(row[0]) + ": " + str(row[1]) + "\n"
		server_.send(self.conn, s)
		return 1


	def send_message(self, message):

		command = """INSERT INTO messages (content, sender_id) VALUES (%s, %s) RETURNING message_id""", (message, self.user_id)
		message_id = db.fetch(command)[0][0]

		command = """INSERT INTO conversation_message (conversation_id, message_id) VALUES (%s, %s)""", (self.current_conv, message_id)
		db.execute(command)


	def leave_conversation(self):
		command = """DELETE FROM user_conversation WHERE (user_id = %s);""", (self.user_id, )
		db.execute(command)

		server_.send(self.conn, " ")


	#разлогиниваемся и прерываем переписку
	def quit(self):
		command = """DELETE FROM logged_in WHERE (user_id = %s);""", (self.user_id, )
		db.execute(command)
		self.conn.close()
		users.remove(self)


class process:

	#потокавая функция: ожидает ввода "\exit", и делает exit(0), 
	#если нет подключенных пользователей
	def exiter(self):
		while 1:
			condition = str(input())
			if condition == "\exit":
				command = """SELECT * FROM logged_in;""", (1, )
				if len(db.fetch(command)) > 0:
					print("Cannot terminate, there are users connected")
					continue
				server_.sock.close()
				print("exiting...")
				exit()


	def handler(self, this_user):
		global users

		while(1):
			if this_user.signed_in == 0:
				this_user.sign_in()
				continue

			data = server_.receive(this_user.conn)
			if (data == "\create"):
				this_user.create_conversation()

			elif (data == "\join"):
				if this_user.join_conversation() == 0:
					continue

				message = server_.receive(this_user.conn)
				while message != "\leave":
					this_user.send_message(message)
					#пробегаемся по всем пользователям; тем, кто состоит в текщей переписке,
					#отправляем это сообщение
					message = this_user.user_name + ": " + message
					for usr in users:
						if (usr.current_conv == this_user.current_conv) and (usr != this_user):
							server_.send(usr.conn, message)
					message = server_.receive(this_user.conn)

				this_user.leave_conversation()

			elif data == "\show":
				this_user.show_available()

			elif (data == "\quit"):
				this_user.quit()
				return

	
	def __init__(self):
		global users

		users = []
		command = """DELETE FROM user_conversation;""", (1, )
		db.execute(command)
		command = """DELETE FROM logged_in;""", (1, )
		db.execute(command)


	def __call__(self):
		global users

		tmp_t = Thread(target=self.exiter, args=())
		tmp_t.start()

		while (1):
			conn, addr = server_.sock.accept()

			tmp_user = user(conn)
			users += [tmp_user]

			tmp_t = Thread(target=self.handler, args=(tmp_user, ))
			tmp_t.start()


prc = process()
prc()
