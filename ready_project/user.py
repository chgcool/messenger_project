import socket
from time import sleep

CORRECT = "correct"

SIGN_IN = "\signin"
CREATE = "\create"
JOIN = "\join"
LOG_OUT = "\logout"
SHOW = "\show"
LEAVE_CONV = "\leave"

class connection_class:

	def __init__(self):
		self.sock = socket.socket()
		self.sock.connect(("127.0.0.1", 14901))	

	def send(self, data):
		self.sock.send(data.encode("utf-8"))

	def receive(self):
		data = self.sock.recv(1024)
		return data.decode("utf-8")


class user_class:

	def sign_in(self, username, password):
		connection.send(SIGN_IN)
		sleep(0.1)


		connection.send(username)
		answer = connection.receive()
		if (answer != CORRECT):
			return answer

		connection.send(password)
		answer = connection.receive()
		return answer

	def create_conversation(self, conv_name):
		connection.send(CREATE)
		sleep(0.1)

		connection.send(conv_name)
		answer = connection.receive()
		return answer

	def send_message(self, message):
		connection.send(message)

	def receive_message(self):
		message = connection.receive()
		return message

	def available_conversations(self):
		connection.send(SHOW)
		sleep(0.1)

		conversations = connection.receive()
		return conversations


	def join_conversation(self, conv_name):
		connection.send(JOIN)
		sleep(0.1)

		connection.send(conv_name)
		answer = connection.receive()
		if answer != CORRECT:
			return (0, answer)

		text = connection.receive()
		return (1, text)
		

	def log_out(self):
		connection.send(LOG_OUT)
		sleep(0.1)

		connection.sock.close()

connection = connection_class()


