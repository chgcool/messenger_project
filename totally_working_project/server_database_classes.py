import socket
from psycopg2 import *

#Класс для отправления и получения данных в формате STRING
class server_class:
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

#создаем экземпляры классов
database = database_class()
server = server_class()
