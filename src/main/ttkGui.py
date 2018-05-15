from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedStyle
from tkinter import messagebox
import math
import threading

TASK_HEIGHT = 40
TASK_DIFF = 10
TASK_HALF_DIFF = math.floor(TASK_DIFF / 2)
TASK_FRAME_HEIGHT = 29

class tkGui:

    def __init__(self, window):
        """
        Constructor for tkGui

        Keyword arguments:
        window -- Tk object, the actual window object.

        Creates:
        two frames, a master frame that holds all widgets, and a task frame that holds all taskButton's
        one entry, placed at the top of the master frame.
        a pop up menu for right click functionality
        All accompanying datastructures, and constants needed for the objects methods.
        """

        # set the window
        self.display = window
        self.display.title("Pan-Do")

        self.theme = ThemedStyle()
        self.theme.theme_use('winxpblue')

        self.style = Style()
        self.style.configure('highlight.TFrame', background='yellow')
        self.style.configure('normal.TFrame', background='white')

        # instanitate the currentTasks list
        self.numTasks = 0
        self.currentTasks = list()
        self.currentButtons = dict()
        self.refreshInUse = False
        self.TEXT_WRAP_LENGTH = 400
        self.entryStrVar = StringVar()

        self.selected = list()
        self.undoList = list()
        self.redoList = list()

        # Create the master frame, task frame, and task entry
        self.masterFrame = Frame(self.display)
        self.masterFrame.pack(fill=BOTH, expand=1)

        # self.taskFrame = Frame(self.masterFrame, background="royal blue")
        self.taskFrame = Frame(self.masterFrame)
        # self.taskEntry = Entry(self.masterFrame, textvariable=self.entryStrVar, font="SegoeUI 13", background="white")
        self.taskEntry = Entry(self.masterFrame, textvariable=self.entryStrVar, font="SegoeUI 13")

        # pack the frames and entry
        self.taskEntry.pack(fill=BOTH)
        self.taskFrame.place(x = 0, y = TASK_FRAME_HEIGHT, relwidth = 1.0, relheight = 1.0)

        # bind addTask() when a user hits "enter" on the Entry
        self.taskEntry.bind('<Return>', self.addTask)
        
        self.popup_menu = Menu(self.display, tearoff=False)
        self.popup_menu.add_command(label="sync", command=lambda: self.forceSyncListener.notify([0]))
        self.popup_menu.add_command(label="deselect", command=lambda: self.deselectAll(0))
        self.popup_menu.add_command(label="cut", command=lambda: self.cut(0))
        self.popup_menu.add_command(label="paste", command=lambda: self.paste(0))
        self.taskEntry.bind("<Button-1>", self.deselectAll)
        self.display.bind("<Button-3>", self.display_do_popup) # windows
        # self.display.bind("<Button-2>", self.display_do_popup) # mac

        #bind copy() and paste() when a user hits "ctrl+c" and "ctrl+v" respectivly
        self.taskFrame.bind('<Configure>', self.updateWrapLength)
        self.display.bind('<Control-c>', self.copy)
        self.display.bind('<Control-v>', self.paste)
        self.display.bind('<Control-x>', self.cut)
        self.display.bind('<Control-z>', self.undo)
        self.display.bind('<Control-y>', self.redo)
        self.display.protocol("WM_DELETE_WINDOW", self.onClose)

    def onClose(self):
        """
        Run's on attempt to close the application
        """
        if messagebox.askokcancel("Quit", "Do you want to close Pan-Do?"):
            self.display.destroy()
    
    def completeTask(self, task):
        """
        Removes the given task from currentTasks and currentButtons
        uses the remove listener to notify middleware that the task
        needs to be removed

        Parameters: 
        task -- string of the task to be removed from the list.
        """
        # print("task: " + str(task))
        # print("currentTasks: " + str(self.currentTasks))
        # print("currentButtons: " + self.currentButtons[task].cget("text"))
        self.undoList.append(["add", [task]])
        chk = self.currentButtons[task]
        chk.destroy()
        del self.currentButtons[task]
        self.currentTasks.remove(task)
        self.refreshDisplay()
        self.remove.notify([task])
        # self.currentTasks.remove(task)

    def addListOfTasks(self, listOfTasks):
        """
        This function is to only be called by Middleware.
        Takes in a list of tasks and determines which of the
        elements are new and which are the same and updates
        currentTasks

        Parameters:
        listOfTasks -- list of updated strings to be added 
        """
        print("adding list of tasks")
        # add tasks to the list of current tasks

        oldTasks = list()
        newTasks = list()

        listOfTasks.reverse() # add new from the top
        print(listOfTasks)
        i = 0
        if (len(self.currentTasks) == len(listOfTasks)):
            for task in listOfTasks:
                if not (task == self.currentTasks[i]):
                    self.currentTasks = listOfTasks
                    if not self.refreshInUse:
                        self.refreshDisplay()
                    break
                i = i + 1
        else:
            self.currentTasks = listOfTasks
            # if not self.refreshInUse:
            self.refreshDisplay()

        print(self.currentTasks)

    def addTask(self, event):
        """
        Adds a task string from the task entry box
        to the currentTasks list. Calls refreshDisplay
        and uses the addlistener to notify middleware that
        a new task has been added

        Parameter:
        event -- the event object when the user presses return
                 on the task entry box
        """
        # add task to list of tasks and get rid of text
        print("adding task")
        taskText = self.taskEntry.get()
        self.entryStrVar.set("")

        if(self.currentTasks.count(taskText) > 0):
            return

        # Notify Task Manager that there is a new task
        self.currentTasks.insert(0, taskText)
        self.refreshDisplay()
        self.undoList.append(["remove", [taskText]])
        self.add.notify([taskText])

    def refreshDisplay(self):
        """
        Takes the list of currentTasks strings and 
        builds new TaskButton objects and places all
        TaskButton objects in their new locations on
        the window.
        """
        print("refreshing Display")

        y = TASK_DIFF
        for task in self.currentTasks:
            if task not in self.currentButtons:
                print(task, "button creation")
                
                chk = TaskButton(self.display, self.taskFrame, task, self.moveTask,
                                                                     self.TEXT_WRAP_LENGTH,
                                                                     self.completeTask,
                                                                     self.editListener,
                                                                     self.editUpdate,
                                                                     self.addUndo,
                                                                     self.select,
                                                                     self.controlSelect,
                                                                     self.shiftSelect,
                                                                     self.deselect,
                                                                     self.deselectAll)
                self.currentButtons[task] = chk
                
            button = self.currentButtons[task]
            button.move(y)
            self.display.update_idletasks() # ensures that everything is displayed correctly
            y = y + button.winfo_height() + TASK_DIFF

    def setCurrentProject(self, project):
        """
            sets the currentProject string

            Parameter:
            project -- the string that currentProject is to be set to
        """
        self.currentProject = project

    def setAddListener(self, listener):
        """
            sets the add function pointer

            Parameter:
            listener -- the function that add is to be set to
        """
        self.add = listener

    def setRemoveListener(self, listener):
        """
            sets the remove function pointer

            Parameter:
            listener -- the function that remove is to be set to
        """
        self.remove = listener

    def setProjectNamesListener(self, listener):
        """
            sets the getProjectNames function pointer

            Parameter:
            listener -- the function that getProjectNames is to be set to
        """
        self.getProjectNames = listener

    def setProjectSwapListener(self, listener):
        """
            sets the swapProjectListener function pointer

            Parameter:
            listener -- the function that swapProjectListener is to be set to
        """
        self.swapProjectListener = listener

    def setSyncListener(self, listener):
        """
            sets the syncListener function pointer

            Parameter:
            listener -- the function that syncListener is to be set to
        """
        self.syncListener = listener

    def setEditListner(self, listener):
        """
            sets the editListener function pointer

            Parameter:
            listener -- the function that editListener is to be set to
        """
        self.editListener = listener

    def setProjectNames(self, projects):
        """
            sets the projectNames list

            Parameter:
            projects: the list of strings of projectNames
        """
        self.projectNames = projects

    def setForceSync(self, listener):
        """
            sets the forceSyncListener function pointer

            Parameter:
            listener -- the function that forceSyncListener is to be set to
        """
        self.forceSyncListener = listener

    def startGui(self):
        """
            Calls mainloop on the display
        """
        # start the display
        self.display.mainloop()

    def displayError(self, error):
        """
            Displays the error message string
        """
        print(error)
        messagebox.showinfo('Pan-Do', error)

    def generateCopyText(self, tasks):
        """
            Generates string from the given list of tasks,
            new tasks seperated newline character

            Parameter:
            tasks: list of task string, seperated by newline character
        """
        ans = ""
        for task in tasks:
            ans = ans + task + '\n'
        
        return ans

    def copy(self, event):
        """
            Generates a list of tasks from selected tasks, and copy them to the clipboard
            When no tasks are selected, copys the whole list of tasks
            Handles ctrl-c event

            Parameter:
            event -- the control-c event
        """
        toCopy = ""
        if len(self.selected) > 0:
            ls = list()
            tasks = self.selected
            for task in tasks:
                ls.append(task)

            toCopy = self.generateCopyText(ls)
            self.deselectAll(False)
        else:
            toCopy = self.generateCopyText(self.currentTasks)

        self.display.clipboard_clear()
        self.display.clipboard_append(toCopy)

    def paste(self, event):
        """
            Handles the control-v event. Takes the string from the user's clipboard, splits it on newline characters and
            adds each seperated string as a new task to the application. Uses the add listener
            to notify middleware.

            Parameter:
            event -- the control-v event
        """
        tasks = self.display.selection_get(selection = "CLIPBOARD").strip()
        tasksAdded = list()
        for task in tasks.splitlines():
            if(self.currentTasks.count(task) == 0):
                tasksAdded.insert(0, task)
                self.currentTasks.insert(0, task)
        
        self.refreshDisplay()
        print("currentTasks: " + str(self.currentTasks))
        self.undoList.append(["add", tasksAdded])
        self.add.notify(tasksAdded)

        # for task in tasksAdded:
        #     print(task)
        #     self.add.notify([task])
            
    def cut(self, event):
        """
            Handles the control-x event. Clears the user's clipboard. Completes all
            of the tasks in the selected list and builds a string of all of the task
            strings to be put into the user's clipboard

            Parameter:
            event -- the control-x event
        """
        tasks = self.selected
        self.display.clipboard_clear()

        for task in tasks:
            chk = self.currentButtons[task]
            chk.destroy()
            del self.currentButtons[task]
            self.currentTasks.remove(task)

        self.refreshDisplay()
        self.remove.notify(tasks)
        self.undoList.append(["add", tasks])
        self.display.clipboard_append(self.generateCopyText(self.selected))
        self.selected = list()

    def editUpdate(self, old, new):
        """
            Updates the old task text in currentTasks and currentButtons to be the new
            edited string

            Parameters:
            old -- the old task string to be updated
            new -- the new task string value
        """
        i = 0
        for task in self.currentTasks:
            if (task == old):
                self.currentTasks[i] = new
                break
            i = i + 1
        
        self.currentButtons[new] = self.currentButtons[old]

    def updateWrapLength(self, event):
        """
            Called when by the configure event. Updates the wraplength of all TaskButtons
            stored in currentButtons. The new wraplength is based off of the event width
            attribute

            Parameter:
            event -- the configure event that contains the new width of the widget
        """
        print("update wrap length")
        for task in self.currentTasks:
            self.TEXT_WRAP_LENGTH = event.width - 25
            button = self.currentButtons[task]
            button.updateWrapLength(self.TEXT_WRAP_LENGTH)

        self.refreshDisplay()

    def undo(self, event):
        """
            Handles the control-z event. Takes the first element from the undoList,
            which is a list, and determines what action to take based off of the first
            element of the inner list.

            Parameter:
            event: the control-z event
        """
        if len(self.undoList) == 0:
            print("nothing to undo")
            return

        undoAction = self.undoList.pop()
        action = undoAction[0]
        if(action == "add"):
            tasks = undoAction[1]

            for task in tasks:
                if (self.currentTasks.count(event) == 0):
                    self.currentTasks.insert(0, task)

            self.refreshDisplay()

            self.redoList.append(["remove", tasks])
            self.add.notify(tasks)

        elif (action == "remove"):
            tasks = undoAction[1] # tasks is a list of tasks that need to be removed

            for task in tasks:
                chk = self.currentButtons[task]
                chk.destroy()
                del self.currentButtons[task]
                self.currentTasks.remove(task)

            self.refreshDisplay() # refresh display before notify call
            self.redoList.append(["add", [task]])
            self.remove.notify([task])

        elif (action == "edit"):
            edits = undoAction[1] # edit is a list of two elements: old and new
            old = edits[0]
            new = edits[1]

            button = self.currentButtons.get(old)
            button.changeTask(new)
            self.editUpdate(old, new)
            self.editListener.notify([old, new])
            self.redoList.append(["edit", [new, old]])
            print("redo list: " + str(self.redoList))
            print("undo list: " + str(self.undoList))
        
        elif (action == "projectSwap"):
            project = undoAction[1] # project is a list of one element

            for task in self.currentTasks:
                button = self.currentButtons[task]
                button.destroy()
                del self.currentButtons[task]

            self.swapProjectListener.notify([project])
            self.redoList.append(["projectSwap", [self.currentProject]])
            self.setCurrentProject(project[0])

    def redo(self, event):
        """
            Handles the control-y event. Takes the first element from the redoList,
            which is a list, and determines what action to take based off of the first
            element of the inner list.

            Parameter:
            event: the control-y event
        """
        if len(self.redoList) == 0 :
            print("nothing to redo")
            return

        redoAction = self.redoList.pop()
        action = redoAction[0]
        if(action == "add"):
            task = redoAction[1]
            self.currentTasks.insert(0, task)
            self.refreshDisplay()
            if(self.currentTasks.count(event) > 0):
                return
            
            self.undoList.append(["remove", task])
            self.add.notify([task])
        
        elif (action == "remove"):
            task = redoAction[1]
            chk = self.currentButtons[task]
            chk.destroy()
            del self.currentButtons[task]
            self.currentTasks.remove(task)
            self.refreshDisplay()
            
            self.undoList.append(["add", task])
            self.remove.notify([task])

        elif (action == "edit"):
            old = redoAction[1]
            new = redoAction[2]

            button = self.currentButtons.get(old)
            button.changeTask(new)
            self.editUpdate(old, new)
            self.editListener.notify([old, new])
            self.undoList.append(["edit", new, old])
            print("redo list: " + str(self.redoList))
            print("undo list: " + str(self.undoList))

        elif (action == "projectSwap"):
            project = redoAction[1]
            for task in self.currentTasks:
                button = self.currentButtons[task]
                button.destroy()
                del self.currentButtons[task]

            self.swapProjectListener.notify([project])
            self.addUndo(["projectSwap", self.currentProject])
            self.currentProject = project

    def addUndo(self, item):
        """
            Adds the item to the end of the undoList.

            Parameter:
            item -- the list of action and arguments to be added
        """
        self.undoList.append(item)

    def addRedo(self, item):
        """
            Adds the item to the end of the redoList.

            Parameter:
            item -- the list of action and arguments to be added
        """
        self.redoList.append(item)

    def select(self, item):
        """
            Adds the item to the selected list
        """
        self.selected.append(item)
        # print("pSelect: " + str(self.selected))

    def controlSelect(self, item):
        """
            handles the control-click event. Adds or removes the item from the selected list
        """
        button = self.currentButtons.get(item)
        isSelected = button.getIsSelected()
        if isSelected:
            self.deselect(item)
            button.deSelect()
            button.changeIsSelected(False)
        else: 
            self.select(item)
            button.select()
            button.changeIsSelected(True)

    def shiftSelect(self, end):
        """
            Determines what tasks should be selected based of 
            what's current being select and what's being shift clicked

            Parameter:
            ending -- end index
        """
        if not len(self.selected) == 0:
            start = self.selected[0]
            startIndex = self.currentTasks.index(start)
            endIndex = self.currentTasks.index(end)
            minDis = abs(startIndex - endIndex)

            for task in self.selected:
                taskIndex = self.currentTasks.index(task)
                distance = abs(taskIndex - endIndex)

                if (distance < minDis):
                    minDis = distance
                    startIndex = taskIndex

            if (startIndex > endIndex):
                temp = startIndex
                startIndex = endIndex
                endIndex = temp

            self.deselectAll(False)         
            self.selectFrom(startIndex, endIndex)

    def selectFrom(self, start, end):
        """
            The beginning of a list selected tasks

            Parameters:
            start -- starting index
            end -- ending index
        """
        i = start
        while (i <= end):
            task = self.currentTasks[i]
            button = self.currentButtons.get(task)
            button.select()
            button.changeIsSelected(True)
            self.selected.append(task)
            i = i + 1
        # print(self.selected)

    def deselect(self, item):
        """
            Remove the task from the selected task list

            Parameter:
            item -- the task
        """
        self.selected.remove(item)
        # print("pDeselect: " + str(self.selected))

    def deselectAll(self, task):
        """
            Deselect all the tasks
        """
        if len(self.selected) == 1 and (task == self.selected[0]):
            return

        for item in self.selected:
            button = self.currentButtons.get(item)
            button.deSelect()
            button.changeIsSelected(False)
        
        self.selected = list()
        # print("pDeselectAll: " + str(self.selected))

    def moveTask(self, dragTask):
        """
            TODO: Move task up and down

            Parameter:
            dragTask -- the current task that's being dragging
        """
        listLen = len(self.currentTasks)
        if(listLen == 1):
            self.refreshDisplay()

        print("drop calculation")
        oldPos = self.currentTasks.index(dragTask)
        drag = self.currentButtons[dragTask]
        dragTop = drag.winfo_y()
        dragMid = dragTop + math.floor(drag.winfo_height() / 2)

        for task in self.currentTasks:
            if (task != dragTask):
                compare = self.currentButtons[task]
                top = compare.winfo_y() - TASK_HALF_DIFF
                bottom = compare.winfo_y() + compare.winfo_height() + TASK_HALF_DIFF
                # print(top, bottom, dragMid, compare.winfo_y(), drag.winfo_y())
                newPos = self.currentTasks.index(task)
                if ((dragMid >= top) and (dragMid < bottom)):
                    # print(task, newPos)
                    self.currentTasks.insert(newPos, self.currentTasks.pop(oldPos))
                    break
                elif (newPos == (listLen - 1)) and (dragMid >= bottom):
                    # print(task, newPos)
                    self.currentTasks.insert(newPos, self.currentTasks.pop(oldPos))
                    break

        self.refreshDisplay()

    def swapProject(self, project):
        """
            Swap to another project

            Parameter:
            project -- the "new" project user desire to swap to
        """
        for task in self.currentTasks:
            button = self.currentButtons[task]
            button.destroy()
            del self.currentButtons[task]

        self.swapProjectListener.notify([project])
        self.addUndo(["projectSwap", [self.currentProject]])
        self.currentProject = project

    def sync(self):
        """
            Calls force sync.
        """
        self.forceSyncListener.notify([''])

    def display_do_popup(self, event):
        """
            Handles the right-click context menu popup.
        """
        self.submenu = Menu(self.popup_menu, tearoff = False)
        self.getProjectNames.notify([0])
        print(self.projectNames, "current project: ", self.currentProject)
        for project in self.projectNames:
            if (project != self.currentProject):
                self.submenu.add_command(label=project,
                                         command=lambda p=project: self.swapProject(p.strip()))

        self.popup_menu.add_cascade(label="swap project",menu=self.submenu)
        
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.delete("swap project")
            self.popup_menu.grab_release()

    def fiveMinuteSync(self):
        """
            Force sync every 5 minutes from when it's boot, 
            regardless of other kinds of sync.
        """
        syncThread = threading.Timer(300.0, self.fiveMinuteSync)
        syncThread.daemon = True
        syncThread.start()
        self.forceSyncListener.notify([''])

class DragDropWidget:
    def __init__(self, *args, **kwargs):
        """
        Initialize method for Drag Drop class
        this class gives a widget vertical drag drop functionality
        """
        super().__init__(*args, **kwargs)
        self.drag_start_y = 0
        self.callNumber = 0

    def drag_start(self, event):
        """
            Initializes the drag

            Parameter:
            event -- the dragging event
        """
        # print("drag start")
        self.drag_start_y = event.y
        # print(self.drag_start_y, event.y, self.winfo_height())

    def drag_motion(self, event):    
        """
            Parameter:
            event -- 
        """    
        self.callNumber = self.callNumber + 1
        if self.callNumber == 5:
            self.callNumber = 0
            y = self.winfo_y() - self.drag_start_y + event.y 
            # print("dragging task: ", "y: ", y, "winfo_y: ", self.winfo_y())
            self.move(y)

    def drop(self, event):
        """
            Calls the tasks button move task function pointer

            Parameter:
            event -- move task event
        """
        # print("dropping task")
        self.moveTask(self.getTaskText())

class TaskButton(DragDropWidget, Frame):
    def __init__(self, window, parent, task, moveTask, textWrapLength, 
                             complete, editListener, editUpdate,
                             addUndo, select, controlSelect,
                             shiftSelect, deselect, deselectAll):
        """
        Constructor for a TaskButton

        Keyword arguments:
        window -- Tk object, the login page interface
        Parent -- Parent widget which this Button will be placed on
        Task   -- String for the text to be displayed
        MoveTask -- function pointer that will be called when task is being moved
        textWrapLength -- length, in pixels, at which the text of the task will be wrapped
        complete -- function pointer which handles the completion of tasks
        editListener -- function pointer which handles notifying middleware of an edit to the task.
        editUpdate -- function pointer which handles updating the GUI's references of the task
        addUndo -- function pointer which handles adding to the undo stack
        addRedo -- function pointer which handles adding to the redo stack
        select -- function pointer which handles adding the task to tkGui's selected list
        controlSelect -- function pointer which handles Control-Click events
        shiftSelect -- function pointer which handles Shift-Click events
        deslect -- function pointer which handles removing the task from tkGui's selected list
        deselectAll -- function pointer which handles removing everything from tkGui's selected list

        Creates:
        Label and Entry for both username and password
        Login button

        """
        DragDropWidget.__init__(self)
        # Frame.__init__(self, parent, background="white")
        Frame.__init__(self, parent, style='normal.TFrame')
        self.moveTask = moveTask
        self.editListener = editListener
        self.editUpdate = editUpdate
        self.addUndo = addUndo
        self.parentSelect = select
        self.controlSelect = controlSelect
        self.shiftSelect = shiftSelect
        self.parentDeselect = deselect
        self.parentDeselectAll = deselectAll
        self.chkVar = IntVar(value=0)
        self.strVar = StringVar(value=task)
        self.wrapLengthRefresh = 0
        self.WrapLength = 0
        self.isSelected = False
        self.firstDisplay = True
        self.chk = Checkbutton(self, variable=self.chkVar, command=lambda t = task: complete(t))
        self.label = Label(self, textvariable=self.strVar, font="SegoeUI 13", wraplength = textWrapLength, justify=LEFT)
        self.editEntry = Entry(self, font="SegoeUI 13")
        self.editEntry.bind('<Return>', lambda e: self.taskMode())

        self.chk.pack(side=LEFT)
        self.label.pack(side=LEFT)

        self.popup_menu = Menu(self, tearoff=False)
        self.popup_menu.add_command(label="complete", command=lambda t = task: complete(t))
        self.popup_menu.add_command(label="edit", command=lambda: self.editMode())
        
        # drag drop binding on frame
        self.bind("<Button-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag_motion)
        self.bind("<ButtonRelease-1>", self.drop)    

        # selection binding on frame
        self.bind("<Double-Button-1>", self.selected)
        self.bind("<Control-Button-1>", lambda e: self.controlSelect(self.strVar.get()))
        self.bind("<Shift-Button-1>", lambda e: self.shiftSelect(self.strVar.get()))
        
        # drag drop binding on label
        self.label.bind("<Button-1>", self.drag_start)
        self.label.bind("<B1-Motion>", self.drag_motion)
        self.label.bind("<ButtonRelease-1>", self.drop)        

        # selection binding on label
        self.label.bind("<Double-Button-1>", self.selected)
        self.label.bind("<Control-Button-1>", lambda e: self.controlSelect(self.strVar.get()))
        self.label.bind("<Shift-Button-1>", lambda e: self.shiftSelect(self.strVar.get()))
        
        # right click context menu binding on label
        self.label.bind("<Button-3>", self.popup) # windows
        # self.label.bind("<Button-2>", self.popup) # mac

    def popup(self, event):
        """
        Event handler for right click events. Brings up the
        right-click popup menu for tasks

        Parameters:
        event -- the event data object
        """
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def editMode(self):
        """
        Puts the TaskButton into edit mode
        """
        # print("edit mode")
        self.label.pack_forget()
        self.editEntry.pack(fill=X)

    def changeTask(self, newText):
        """
        changes the text of the label widget using a
        string variable object.

        Parameters:
        newText -- the new text to be displayed
        """
        self.strVar.set(newText)
        self.configure()

    def taskMode(self):
        """
        Updates the task with edited text and 
        returns the TaskButton to taskMode
        """
        # print("task mode")
        old = self.getTaskText()
        new = self.editEntry.get()
        self.changeTask(new)
        self.editEntry.delete(0, END)
        self.editEntry.pack_forget()
        self.changeTask(new)
        self.editUpdate(old, new)
        self.label.pack(side=LEFT)
        self.label.configure(wraplength = self.WrapLength)
        self.addUndo(["edit", [new, old]]) # undo the edit. 'new' is now the old content to be reverted
        self.editListener.notify([old, new])

    def changeIsSelected(self, val):
        """
        updates self.isSelected to the given value

        Parameters:
        val -- a boolean to change isSelected to.
        """
        self.isSelected = val     
    
    def select(self):
        """
        highlights the TaskButton in yellow
        """
        self.configure(style="highlight.TFrame")
        self.label.configure(style="highlight.TFrame")

    def deSelect(self):
        """
        highlights the TaskButton in white
        """
        self.configure(style="normal.TFrame")
        self.label.configure(style="normal.TFrame")

    def selected(self, event):
        """
        handles the double left click event to select
        the task

        Parameters:
        event -- the event object for the double left click
        """
        # print("selected", self.isSelected)
        self.parentDeselectAll(self.getTaskText())
        if self.isSelected:
            # print("being deslected")
            self.parentDeselect(self.getTaskText())
            self.deSelect()
            self.changeIsSelected(False)
        else:
            # print("being selected")
            self.parentSelect(self.getTaskText())
            self.select()
            self.changeIsSelected(True)

    def getTaskText(self):
        """
        returns a string with thet text of the Task
        """
        return self.label.cget("text")

    def getIsSelected(self):
        """
        returns the value of self.isSelected
        Should always be a boolean
        """
        return self.isSelected

    def move(self, y):
        """
        Moves the TaskButton to the given y-coordinate
        using the tkinter .place() method

        Parameter:
        y -- the y position that the TaskButton is
             to be moved to
        """
        self.place(x = 0, y = y, relwidth = 1.0)

    def updateWrapLength(self, width):
        """
        updates the TaskButton label's wraplength 
        to the given width. It only refreshes every
        20 calls.

        Parameter:
        width -- the width, in pixels, of the new wrap length of the label widget
        """
        self.wrapLengthRefresh = self.wrapLengthRefresh + 1
        if (self.wrapLengthRefresh % 20) == 0:
            self.wrapLengthRefresh = 0
            self.WrapLength = width
            self.label.configure(wraplength=width)

