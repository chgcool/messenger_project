import socket
from psycopg2 import *
from threading import Thread
from sys import exit

CORRECT = "correct"

SIGN_IN = "\signin"
CREATE = "\create"
JOIN = "\join"
LOG_OUT = "\logout"
SHOW = "\show"
LEAVE_CONV = "\leave"

STOP_SERVER = "\exit"


#Класс для отправления и получения данных в формате STRING
class server_class:
	sock = None

	def __init__(self):
		self.sock = socket.socket()
		self.sock.bind(("localhost", 14901))
		self.sock.listen(10)


	def send(self, conn, data):
		conn.send(data.encode("utf-8"))


	def receive(self, conn):
		data = conn.recv(1024)
		return data.decode("utf-8")

	def __del__(self):
		self.sock.close()


#класс для связи с базой данных
class database_class:

	database_connection = None
	cursor = None

	def __init__(self):
		con_str = "dbname = 'messenger' user = 'svyatoslav' host = 'localhost' password = 'Genetika1'"
		self.database_connection = connect(con_str)
		self.cursor = self.database_connection.cursor()

	#функция с возвратом, для выборок
	def fetch(self, command):
		self.cursor.execute(*command)
		self.database_connection.commit()
		rows = self.cursor.fetchall() 
		return rows

	#без возврата, только для вставки, удаления и т.д.
	def execute(self, command):
		self.cursor.execute(*command)
		self.database_connection.commit()


	def clear_user_conversation(self):
		command = """DELETE FROM user_conversation;""", (1, )
		self.execute(command)

	def clear_logged_in(self):
		command = """DELETE FROM logged_in;""", (1, )
		self.execute(command)


	def check_username(self, username):
		#проверка на существование
		command = """SELECT * FROM users WHERE user_name = %s;""", (username, )
		rows = self.fetch(command)
		if len(rows) == 0:
			return 0

		#проверка на повторный вход
		command = """SELECT * FROM logged_in WHERE user_name = %s;""", (username, )
		if len(self.fetch(command)) > 0:
			return 0

		return 1

	def check_password(self, username, password):
		command = """SELECT user_id FROM users WHERE (user_name = %s) AND (password = %s);""", (username, password)
		rows = self.fetch(command)
		if len(rows) == 0:
			return -1
		return rows[0][0]

	def add_into_logged_in(self, user_id, username):
		command = """INSERT INTO logged_in (user_id, user_name) VALUES (%s, %s);""", (user_id, username)
		self.execute(command)


	def conversation_exists(self, conv_name):
		command = """SELECT * FROM conversations WHERE (conversation_name = %s);""", (conv_name, )
		return (len(self.fetch(command)) > 0)

	def insert_conversation(self, conv_name):
		command = """INSERT INTO conversations (conversation_name) VALUES (%s);""", (conv_name, )
		self.execute(command)


	def all_conversations(self):
		command = """SELECT conversation_name FROM conversations;""", (1, )
		rows = database.fetch(command)
		return rows

	def get_conversation_id(self, conv_name):
		command = """SELECT * FROM conversations WHERE (conversation_name = %s);""", (conv_name, )
		rows = self.fetch(command)
		if len(rows) == 0:
			return -1
		return rows[0][0]

	def join_conversation(self, user_id, conversation_id):
		command = """INSERT INTO user_conversation VALUES (%s, %s)""", (user_id, conversation_id)
		self.execute(command)

	def messages_in_conversation(self, conversation_id):
		command = """SELECT user_name, content FROM 
			(SELECT sender_id AS user_id, delivery_time, content FROM 
			(SELECT * FROM conversation_message WHERE conversation_id = %s) a
			JOIN messages USING (message_id)) b
			JOIN users USING (user_id) ORDER BY b.delivery_time;""", (conversation_id, )

		return self.fetch(command)

	def store_message(self, message, sender_id, conversation_id):
		command = """INSERT INTO messages (content, sender_id) VALUES (%s, %s) RETURNING message_id""", (message, sender_id)
		message_id = database.fetch(command)[0][0]

		command = """INSERT INTO conversation_message (conversation_id, message_id) VALUES (%s, %s)""", (conversation_id, message_id)
		self.execute(command)


	def leave_conversation(self, user_id):
		command = """DELETE FROM user_conversation WHERE (user_id = %s);""", (user_id, )
		self.execute(command)


	def log_out(self, user_id):
		command = """DELETE FROM logged_in WHERE (user_id = %s);""", (user_id, )
		self.execute(command)

	def number_of_logged_in(self):
		command = """SELECT * FROM logged_in;""", (1, )
		return len(self.fetch(command))



#класс подключенного пользователя, 
#с данными о нем и функциями для общения через socket
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
		signed_in = 0


	def sign_in(self):
		username = server.receive(self.conn)
		correct = database.check_username(username)
		if not correct:
			server.send(self.conn, "wrong username")
			return	
		server.send(self.conn, CORRECT)

		password = server.receive(self.conn)
		print(password)
		user_id = database.check_password(username, password)
		if user_id == -1:
			server.send(self.conn, "wrong password")
			return
		server.send(self.conn, CORRECT)
		print("that's it")

		#все, логин и пароль правильные

		self.user_id = user_id
		self.user_name = username
		self.signed_in = 1

		database.add_into_logged_in(user_id, username)

		print("user " + str(self.user_id) + " signes in\n")


	def create_conversation(self):
		conv_name = server.receive(self.conn)

		if database.conversation_exists(conv_name):
			server.send(self.conn, "conversation already exists")
			return		

		database.insert_conversation(conv_name)
		server.send(self.conn, "created")


	def show_available(self):
		rows = database.all_conversations()

		result = ""
		for row in rows:
			result += row[0] + "\n"

		server.send(self.conn, result)


	def join_conversation(self):

		conv_name = server.receive(self.conn)

		if not database.conversation_exists(conv_name):
			server.send(self.conn, "there is no such conversation")
			return 0

		server.send(self.conn, CORRECT)

		self.current_conv = database.get_conversation_id(conv_name)
		database.join_conversation(self.user_id, self.current_conv)

		#выводим все ранее нотправленные сообщения
		text = database.messages_in_conversation(self.current_conv)
		s = "---\n"
		for row in text:
			s += str(row[0]) + ": " + str(row[1]) + "\n"
		server.send(self.conn, s)

		return 1


	def send_message(self, message):
		database.store_message(message, self.user_id, self.current_conv)


	def leave_conversation(self):
		database.leave_conversation(self.user_id)

		#nehoroshiy kostyl
		server.send(self.conn, " ")


	#разлогиниваемся и прерываем переписку
	def quit(self):
		database.log_out(self.user_id)
		self.conn.close()


class main_handler:

	#потокавая функция: ожидает ввода "\exit", и делает exit(0), 
	#если нет подключенных пользователей
	def exiter(self):
		while 1:
			condition = str(input())
			if condition == STOP_SERVER:
				if database.number_of_logged_in() > 0:
					print("Cannot terminate, there are users connected")
					continue
				server.sock.close()
				print("exiting...")
				exit(0)


	def handler(self, this_user):
		while(1):
			data = server.receive(this_user.conn)

			if (data == SIGN_IN):
				this_user.sign_in()
			
			elif (data == CREATE):
				this_user.create_conversation()

			elif (data == JOIN):
				if this_user.join_conversation() == 0:
					continue

				message = server.receive(this_user.conn)
				while message != LEAVE_CONV:
					this_user.send_message(message)
					
					#пробегаемся по всем пользователям; тем, кто состоит в текщей переписке, отправляем это сообщение
					message = this_user.user_name + ": " + message
					for usr in self.users:
						if usr.current_conv == this_user.current_conv:
							server.send(usr.conn, message)
					message = server.receive(this_user.conn)

				this_user.leave_conversation()

			elif data == SHOW:
				this_user.show_available()

			elif (data == LOG_OUT):
				self.users.remove(this_user)
				this_user.quit()
				return

	
	def __init__(self):
		self.users = []
		database.clear_user_conversation()
		database.clear_logged_in()


	def start_server(self):

		main_thread = Thread(target=self.exiter, args=())
		main_thread.start()

		while (1):
			conn, addr = server.sock.accept()

			this_user = user(conn)
			self.users += [this_user]

			user_thread = Thread(target=self.handler, args=(this_user, ))
			user_thread.start()


if __name__ == "__main__":
	#создаем экземпляры классов
	database = database_class()
	server = server_class()

	#и поехали
	mh = main_handler()
	mh.start_server()

