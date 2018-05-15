from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedStyle
from pytodoist import todoist
import keyring
import webbrowser

class tkLogin:

    def __init__(self, window, listener):
        """
        Constructor for the Login

        Keyword arguments:
        window -- Tk object, the login page interface
        login -- login listener

        Creates:
        Label and Entry for both username and password
        Login button

        """
        self.font = "SogeoUI 15"

        self.loginListener = listener
        self.display = window
        self.display.title("Pan-Do")

        self.style = ThemedStyle()
        self.style.theme_use('winxpblue')

        self.loginFrame = Frame(self.display)
        self.urnmStrVar = StringVar()
        self.pswdStrVar = StringVar()
        self.usernameEntry = Entry(self.loginFrame, textvariable = self.urnmStrVar, font = self.font)
        self.usernameLabel = Label(self.loginFrame, text = "Username", font = self.font)
        self.passwordEntry = Entry(self.loginFrame, textvariable = self.pswdStrVar, show = "•", font = self.font)
        self.passwordLabel = Label(self.loginFrame, text = "Password", font = self.font)

        self.loginButton = Button(self.loginFrame, text = "Login", command = self.login)
        self.signUpButton = Button(self.loginFrame, text = "Sign Up", command = lambda: self.displaySignUpPage())
        self.forgotPasswordLabel = Label(self.loginFrame, text = "Forgot Password?", font = self.font)

        # this is for the register widget
        self.fullNameEntry = Entry(self.loginFrame, font = self.font)
        self.fullNameLabel = Label(self.loginFrame, text = "Full Name ", font = self.font)
        self.emailEntry = Entry(self.loginFrame, font = self.font)
        self.emailLabel = Label(self.loginFrame, text = "Email Address ", font = self.font)
        self.signUpPasswordEntry = Entry(self.loginFrame, font = self.font)
        self.signUpPasswordLabel = Label(self.loginFrame, text = "Password ", font = self.font)
        
        self.registerButton = Button(self.loginFrame, text = "Register Account", command =lambda: self.register(self.fullNameEntry.get(),
                                                                                                         self.emailEntry.get(),
                                                                                                         self.signUpPasswordEntry.get()))
        self.cancelRegisterButton = Button(self.loginFrame, text = "Cancel", command = lambda: self.backToLoginPage())
        
        #display login
        self.usernameLabel.grid(row = 0, column = 0)
        self.usernameEntry.grid(row = 0, column = 1)
        self.passwordLabel.grid(row = 1, column = 0)
        self.passwordEntry.grid(row = 1, column = 1)
        self.loginButton.grid(row = 2, column = 0)
        self.signUpButton.grid(row = 2, column = 1)
        self.forgotPasswordLabel.grid(row = 3, column = 0)

        self.loginFrame.pack(fill = 'both')

        self.passwordEntry.bind('<Return>', self.loginEvent)
        self.forgotPasswordLabel.bind('<Button-1>', self.forgotPassword)

    def displaySignUpPage(self):
        """
        Sign Up page gets displayed here

        First ungrid login widgets, then grid existing register widgets
        """
        self.usernameEntry.grid_remove()
        self.usernameLabel.grid_remove()
        self.passwordEntry.grid_remove()
        self.passwordLabel.grid_remove()
        self.loginButton.grid_remove()
        self.forgotPasswordLabel.grid_remove()
        self.signUpButton.grid_remove()

        self.fullNameLabel.grid(row = 0, column = 0)
        self.fullNameEntry.grid(row = 0, column = 1)
        self.emailLabel.grid(row = 1, column = 0)
        self.emailEntry.grid(row = 1, column = 1)
        self.signUpPasswordLabel.grid(row = 2, column = 0)
        self.signUpPasswordEntry.grid(row = 2, column = 1)
        self.registerButton.grid(row = 3, column = 0)
        self.cancelRegisterButton.grid(row = 3, column = 1)

        self.signUpPasswordEntry.bind('<Return>', self.register)

    def register(self, fullName, email, password):
        """
        Register new user using Todoist register

        """
        self.user = todoist.register(fullName, email, password, lang=None, timezone=None)
        # self.backToLoginPage()
        self.loginAfterSignedUp()

    def backToLoginPage(self):
        """
        Bring back the login page

        """
        self.fullNameLabel.grid_remove()
        self.fullNameEntry.grid_remove()
        self.emailLabel.grid_remove()
        self.emailEntry.grid_remove()
        self.signUpPasswordLabel.grid_remove()
        self.signUpPasswordEntry.grid_remove()
        self.registerButton.grid_remove()
        self.cancelRegisterButton.grid_remove()

        self.usernameLabel.grid(row = 0, column = 0)
        self.usernameEntry.grid(row = 0, column = 1)
        self.passwordLabel.grid(row = 1, column = 0)
        self.passwordEntry.grid(row = 1, column = 1)
        self.loginButton.grid(row = 2, column = 0)
        self.signUpButton.grid(row = 2, column = 1)
        self.forgotPasswordLabel.grid(row = 3, column = 0)

    def userLogin(self, username, password):
        """
        Login using Todoist login functionality

        """
        try:
            self.user = todoist.login(username, password)
            # print(self.user)
            f = open("user.txt","w+")
            f.write(username)
            f.close

            keyring.set_password("Pando", username, password)

            self.quit()
        except Exception:
            self.displayError("")

    def signUp(self, full_name, email, password):
        """
        Register new account using Todoist api
        """
        try:
            self.user = todoist.register(full_name, email, password, lang = None, timezone = None)
            self.quit()
        except Exception:
            self.displayError("Unable to sign up")

    def forgotPassword(self, event):
        """
        Direct to Todoist forget you password webpage
        https://todoist.com/Users/forgotPassword
        """
        webbrowser.open_new(r"https://todoist.com/Users/forgotPassword")

    def loginAfterSignedUp(self):
        """
        Login the newly registered user after they signed up
        """
        usernameText = self.emailEntry.get()
        passwordText = self.signUpPasswordEntry.get()

        self.emailEntry.delete(0, END)
        self.signUpPasswordEntry.delete(0, END)

        self.userLogin(usernameText, passwordText)

    def loginEvent(self, event):
        """
        Login functionality that takes an event
        """
        usernameText = self.usernameEntry.get()
        passwordText = self.passwordEntry.get()

        self.usernameEntry.delete(0, END)
        self.passwordEntry.delete(0, END)

        self.userLogin(usernameText, passwordText)

    def login(self):
        """
        Login functionality
        """
        usernameText = self.usernameEntry.get()
        passwordText = self.passwordEntry.get()

        self.usernameEntry.delete(0, END)
        self.passwordEntry.delete(0, END)

        self.userLogin(usernameText, passwordText)
    
    def displayError(self, msg):
        """
        Display a label notifying the user when detected incorrect username or password input
        """
        if not msg:
            errorMsg = "Wrong username or password"
            self.errorLabel = Label(self.display, text = errorMsg)
        else:
            self.errorLabel = Label(self.display, text = msg)

        self.errorLabel.pack()

    def startGui(self):
        """
        Start the login page
        """
        self.display.mainloop()
        # print(self.user)
        # return self.user

    def quit(self):
        """
        Exit out of the login page after logged in
        """
        self.loginListener.notify(self.user)
        self.display.destroy()