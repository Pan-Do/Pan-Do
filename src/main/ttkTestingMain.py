# import ToDoLogin
import middleware
# import TkinterGui
import ttkLogin # the new version of ToDoLogin
import ttkGui # the new version of TkinterGui
import keyring
from pytodoist import todoist
from listeners import *
from tkinter import *
from tkinter import ttk

user = False
def getUser(gotUser):
    global user
    user = gotUser



try:
    userNameFile = open("user.txt", "r")
    userName = userNameFile.read()
    userNameFile.close()
    print(userName)
    if userName !="":
        returnedPassword = keyring.get_password("Pando", userName)
        if returnedPassword!=None:
            try:
                print("Username: "+userName+"\n"+"Password: "+returnedPassword)
                user = todoist.login(userName, returnedPassword)
            # print(self.user)
            except Exception:
                print(Exception)
        else:
            root = Tk()
            listener = LoginListener(getUser)
            # login = ToDoLogin.tkLogin(root, listener)
            login = ttkLogin.tkLogin(root, listener)
            login.startGui()
    else:
        root = Tk()
        listener = LoginListener(getUser)
        # login = ToDoLogin.tkLogin(root, listener)
        login = ttkLogin.tkLogin(root, listener)
        login.startGui()
except:
    root = Tk()
    listener = LoginListener(getUser)
    # login = ToDoLogin.tkLogin(root, listener)
    login = ttkLogin.tkLogin(root, listener)
    login.startGui()


if (user):
    root = Tk()
    root.geometry('400x400')
    # gui = TkinterGui.tkGui(root)
    gui = ttkGui.tkGui(root)
    taskManager = middleware.TaskManager(gui, user)
    taskManager.startGui()
