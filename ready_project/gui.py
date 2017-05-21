from user1 import *
from tkinter import *
from threading import Thread, Event

class log_in:

	def create_fields(self):

		self.login_box = Entry(self.root)
		self.login_box.pack()
		self.login_box.focus_set()

		self.password_box = Entry(self.root)
		self.password_box.pack()
		self.password_box.focus_set()	


	def check(self):
		username = self.login_box.get()
		password = self.password_box.get()

		answer = user.sign_in(username, password)
		if answer == CORRECT:
			self.logged_in = 1
			self.__del__()
			return
		Label(self.root, text=answer).pack()


	def __init__(self, root):
		self.logged_in = 0

		self.master = root
		self.master.withdraw()

		self.root = Toplevel(self.master)
		self.root.title("You have to log in!")
		self.create_fields()

		Button(self.root, text="OK", command=self.check).pack()
		self.root.wait_window()

	def __del__(self):
		self.root.destroy()
		if not self.logged_in:
			self.master.destroy()
			user.log_out()
			return
		self.master.deiconify()


class show_conversations:

	def __init__(self, root):
		self.master = root
		self.master.withdraw()

		self.root = Toplevel(self.master)
		self.text = Text(self.root)
		self.text.pack()
		self.text.insert(END, user.available_conversations())

		self.root.wait_window()

	def __del__(self):
		self.root.destroy()
		self.master.deiconify()


class create_conversation:

	def enter(self):
		conv_name = self.text.get()
		answer = user.create_conversation(conv_name)
		Label(self.root, text=answer).pack()

	def __init__(self, root):
		self.master = root
		self.master.withdraw()

		self.root = Toplevel(self.master)
		self.root.title("creating conversation")
		Label(self.root, text="enter conversation name").pack()
		Button(self.root, text="OK", command=self.enter).pack()
		self.text = Entry(self.root)
		self.text.pack()

		self.root.wait_window()

	def __del__(self):
		self.root.destroy()
		self.master.deiconify()


class messagebox:

	def receiver(self):
		while self.chatting == 1:
			self.conversation.insert(END, user.receive_message() + "\n")
		self.event.set()

	def send(self):
		message = self.message.get()
		user.send_message(message)
		if message == LEAVE_CONV:
			self.chatting = 0
			self.__del__()			


	def __init__(self, root, text):
		self.chatting = 1
		self.event = Event()
		self.master = root
		self.root = Toplevel(self.master)
		self.root.title("It's working! Ain't it cool?")

		self.message = Entry(self.root)
		self.message.bind('<Return>', lambda e:self.send())
		self.message.pack()

		self.conversation = Text(self.root)
		self.conversation.insert(END, text)
		self.conversation.pack()

		Button(self.root, text='send', command=self.send).pack()

		Thread(target=self.receiver, args=()).start()

		self.root.wait_window()

	def __del__(self):
		self.event.wait()
		self.root.destroy()
		self.master.deiconify()


class join_conversation:

	def enter(self):
		conv_name = self.text.get()
		success, answer = user.join_conversation(conv_name)
		if not success:
			Label(self.root, text=answer).pack()
			return
		self.root.destroy()
		messagebox(self.master, answer)


	def __init__(self, root):
		self.master = root
		#self.master.withdraw()

		self.root = Toplevel(self.master)
		self.root.title("joining conversation")
		Label(self.root, text="enter conversation name").pack()
		Button(self.root, text="OK", command=self.enter).pack()
		self.text = Entry(self.root)
		self.text.pack()

		self.root.wait_window()

	def __del__(self):
		self.root.destroy()


class main_window:

	def place_buttons(self):
		show = Button(self.root, text="show available conversations")
		show['command'] = self.show_conversations_
		show.pack()
		print(user.available_conversations())

		join = Button(self.root, text="join conversation")
		join['command'] = self.join_conversation_
		join.pack()

		create = Button(self.root, text="create conversation")
		create['command'] = self.create_conversation_
		create.pack()

	def log_in_(self):
		log_in(self.root)

	def show_conversations_(self):
		show_conversations(self.root)

	def join_conversation_(self):
		join_conversation(self.root)

	def create_conversation_(self):
		create_conversation(self.root)


	def __init__(self):
		self.root = Tk()
		self.root.title("Welcome to our pitiful messanger!")
		self.log_in_()
		self.place_buttons()
		self.root.mainloop()

	def __del__(self):
		user.log_out()


if __name__ == "__main__":
	user = user_class()
	main_window()


