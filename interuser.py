import socket
import threading
from tkinter import *

class client:
    sock = None

    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect(("127.0.0.1", 14900))

    def send(self, data):
        self.sock.send(data.encode("utf-8"))

    def receive(self):
        data = self.sock.recv(1024)
        return data.decode("utf-8")

        # def __del__(self):
        #   self.sock.close()


class user:

    signed_in = None
    connection = None
    chatting = 0

    def __init__(self):
        self.event = threading.Event()
        self.signed_in = 0
        chatting = 0
        self.connection = client()

    def sign_in(self):

        def check():
            username = str(e1.get())
            password = str(e2.get())

            self.connection.send(username)

            self.connection.receive()

            self.connection.send(password)

            answer = self.connection.receive()

            print(answer)

            Label(root, text=answer).grid(row=3)
            if answer == "you've signed in":
                root.quit()

        root = Tk()

        Label(root, text = "username").grid(row = 0, column = 0)
        e1 = Entry(root)
        e1.grid(row = 0, column = 1)

        Label(root, text = "password").grid(row = 1, column = 0)
        e2 = Entry(root)
        e2.grid(row = 1, column = 1)

        Button(root, text = "check", command = check).grid(row = 1, column = 2)
        root.mainloop()


    def create_conversation(self):
        self.connection.send("\create")

        print("name your conversation: ", end='')
        conv_name = str(input())
        self.connection.send(conv_name)

        if self.connection.receive() == "true":
            print("successful")
        else:
            print("conversation already exists")



    def receiver(self):
        while self.chatting == 1:
            print(self.connection.receive())
        self.event.set()


    def show_available(self):
        self.connection.send("\show")

        conversations = self.connection.receive()
        print("available conversations:\n", conversations, sep='')


    def join_conversation(self):
        self.connection.send("\join")

        print("conversation name: ", end='')
        conv_name = str(input())
        self.connection.send(conv_name)

        answer = self.connection.receive()

        if answer != "true":
            print(answer)
            return
        
        print("successful")
        print("type \leave to leave conversation")

        text = self.connection.receive()
        print(text)
        
        self.chatting = 1
        tmp_t = threading.Thread(target=self.receiver, args=())
        tmp_t.start()

        while 1:
            message = str(input())
            self.connection.send(message)
            if message == "\leave":
                self.chatting = 0
                self.event.wait()
                break

        print("You've left conversation")


    def quit(self):
        self.connection.sock.close()
        exit(0)

    def __call__(self):

        def f1():
            self.create_conversation()

        def f2():
            self.join_conversation()

        def f3():
            self.show_available()

        def f4():
            self.quit()

        root2 = Tk()
        Button(root2, text = "create", command = f1).grid(row = 0)
        Button(root2, text = "join", command = f2).grid(row = 1)
        Button(root2, text = "show", command = f3).grid(row = 2)
        Button(root2, text = "quit", command = f4).grid(row = 3)
        root2.mainloop()

usr = user()
usr.sign_in()
usr()





