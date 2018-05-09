# Pan-Do
Desktop widget for Windows 10 based on Todoist api.
## Installation
  > The installed is in the root folder named "Pan-Do Installer". Click to download Pan-Do Installer, then install it on your desktop.
## How to use Pan-Do

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
That take in a Listener class.  The listener class has the structure of having a single `.notify(vals)` method.  The vals is a list, whose structure depends what information the method passed into the listener accepts.  

It also requires the method
gui.setCurrentProject(self.get_project().name)
That takes in the current projects name

And
gui.addListOfTasks([t.content for t in tasks])
That takes in the list of strings for the names of the tasks

It also can require the methods, but they are currently commented out
gui.please_wait()
gui.stop_waiting()

Which are how the middleware communicates to the GUI to stop or resume accepting inputs.  This is used to prevent the application from getting kicked from the Todoist servers
Requires the
gui.displayError(“error”)

So that the middleware can tell the gui when an error occured

And lastly
gui.startGui()
This is how the middleware tells the GUI that it has finished passing what info it needs to pass to the GUI, and the GUI can now start.
Queue and PingLimit
The middleware utilizes an execution queue and a max ping limit to allow it to control how many times the server is pinged.  Since the Todoist API limits the amount of sync requests per minute to 50, and the API we are using to talk to the Todoist API does a sync almost every time a method is called, we keep track of how many pings happen within a minute, and if it approaches 50, it will halt the queue and tell the GUI to inform the user to wait.  After a minute has passed it will reset the counter to 0 and tell the GUI to resume.

## GUI



