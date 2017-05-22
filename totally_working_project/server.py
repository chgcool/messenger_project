from server_database_classes import *
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
		user_id = database.check_password(username, password)
		if user_id == -1:
			server.send(self.conn, "wrong password")
			return
		server.send(self.conn, CORRECT)

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
		server.send(self.conn, LEAVE_CONV)


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
				print(message)
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

	#и поехали
	mh = main_handler()
	mh.start_server()

