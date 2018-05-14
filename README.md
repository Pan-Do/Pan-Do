# Pan-Do
Desktop widget for Windows 10 based on Todoist api.

## Authors
  John Hamilton (Electrum)  
  Andrew Pokorny  
  Yujia Wu (Emelye)  
  Joe Malik  

## Installation
  > The installed is in the root folder named "Pan-Do Installer". Click to download Pan-Do Installer, then install it on your desktop.
## How to use Pan-Do
>1. After installing Pan-Do, click on the icon, a login page will pop up.   
![](screenshots/Figure_1.png)

>2. Enter your email address as Username if you already had an account then click "Login", otherwise, click on "Register New Account", it will take you to the sign up page. "Forgot Password" will take you to a web page to get you your password back. 


>3. "Back to Login" will take you back to the Login Page, "Sign Up" will register a new Todoist account for you and directly take you to the todo-list main page:  
![](screenshots/Figure_2.png)


>4. This is the main page, add new task is at the top, by hitting the Enter key, new task will be added from the top.  
![](screenshots/Figure_3.png)

>5. Complete a Task: 1) Left click on the checkbox in the front of the task, or 2) Right click on the task then select "Complete".

>6. If you need to edit a task, select "Edit", then perform the editing.   
![](screenshots/Figure_4.png)

>7. Right click on either "Add Task" bar on the top, or on the title bar.  
![](screenshots/Figure_5.png)

>8. To force sync, click "Sync".

>9. To deselect when multiple tasks are selected, click "Deselect".

>10. Pan-Do also supports basic keyboard functionalities, but if you want to cut and paste from the widget, click on the corresponding bars. 

>11. To swap to another project, hover over "Swap Project", then choose your desired project.  
![](screenshots/Figure_6.png)


## Middleware
  >The middleware is designed in a way that separates it from the GUI. It takes in a class object in its constructor that has certain requirements.  This is how it interacts with the GUI.

### Methods
```
gui.setAddListener(add)
gui.setRemoveListener(delete)
gui.setProjectSwapListener(projectSwap)
gui.setProjectNamesListener(setProjectNames)
gui.setForceSync(forceSync)
gui.setEditListner(edit)
gui.setTaskMovedListener(moveTask)  
```
That take in a Listener class. The listener class has the structure of having a single `.notify(vals)` method. The vals is a list, whose structure depends what information the method passed into the listener accepts.  

It also requires the method   
`gui.setCurrentProject(self.get_project().name)`  
which takes in the current projects name

And   
`gui.addListOfTasks([t.content for t in tasks])`  
which takes in the list of strings for the names of the tasks

It also can require the methods, but they are currently commented out  
`gui.please_wait()`  
`gui.stop_waiting()`

Which are how the middleware communicates to the GUI to stop or resume accepting inputs.  This is used to prevent the application from getting kicked from the Todoist servers
Requires the `gui.displayError(“error”)`

So that the middleware can tell the gui when an error occured

And lastly  
`gui.startGui()`  
This is how the middleware tells the GUI that it has finished passing what info it needs to pass to the GUI, and the GUI can now start.

### Queue and PingLimit

The middleware utilizes an execution queue and a max ping limit to allow it to control how many times the server is pinged.  Since the Todoist API limits the amount of sync requests per minute to 50, and the API we are using to talk to the Todoist API does a sync almost every time a method is called, we keep track of how many pings happen within a minute, and if it approaches 50, it will halt the queue and tell the GUI to inform the user to wait.  After a minute has passed it will reset the counter to 0 and tell the GUI to resume.

## GUI
The GUI is built with the intention of keeping it completely seperate from middleware class. The GUI class needs to take in all of the required listeners in order to be able to notify the middleware when an action is performed so that the middleware can take the necessary actions needed to keep the todoist servers up to day. This particular GUI runs using tkinter exclusively. It does not user ttk even though there are some files here that are titled as such they are not used when running [main.py](src/main/main.py) 

There are two main classes present in this GUI. The tkGUI and TaskCanvas classes. tkGUI acts as the manager of root TK() object that is its passed, as well as all of the TaskCanvas objects that it creates to handle the tasks themselves.

### tkGui
tkGui is the class that manages the TK window object as well as all of the TaskCanvas objects. For the most part it also handles the notification of the middleware when events occur on the GUI. tkGui keeps track of the order of the tasks, the TaskCanvas' it has created and all of the TaskCanvas' that have reported that they are selected.
### TaskCanvas
TaskCanavas inherits from the tkinter Canvas widget and the DragDropWidget that is defined right above it in the [TkinterGui.py](src/main/TkinterGui.py) file. The DragDropWidget does exactly as the name implies. It implements the Drag and Drop functionality present in the application. 

The TaskCanvas class has the responsibility of managing a single task to be displayed on the window. Upon initialization the TaskCanvas takes in a number of functions. These functions are either a listener or a method given to it by the creator to call when a particular event occurs.
