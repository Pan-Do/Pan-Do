from tkinter import *
from tkinter import messagebox
import math
import threading

from winreg import *

import os
import sys
import win32api
import win32con
import win32gui_struct
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

TASK_HEIGHT = 40
TASK_DIFF = 0
TASK_HALF_DIFF = math.floor(TASK_DIFF / 2)
TASK_FRAME_HEIGHT = 24
CHECK_FILL_COLOR = "#FFFFFF"
CHECK_OUTLINE_COLOR = "#E84D00"
CHECK_HOVER_FILL_COLOR = "#E84D00"
CHECK_HOVER_OUTLINE_COLOR = "#000000"
TASK_BACKGROUND_COLOR = "#D3D3D3"
TASK_SELECTED_COLOR = "#FFFC7C"
BACKGROUND_COLOR = "#D3D3D3"
TEXT_COLOR = "#000000"
DARK_MODE_ON = False
ACCENT_COLOR_ON = False
Main_Color_Dictionary = {"CFC": "#FFFFFF", "COC": "#E84D00", "CHFC": "#E84D00", "CHOC": "#000000", "TBC": "#D3D3D3", "TSC": "#FFFC7C", "BC": "#D3D3D3", "TC":"#000000"}
Dark_Color_Dictionary = {"CFC": "#AAAAAA", "COC": "#E84D00", "CHFC": "#E84D00", "CHOC": "#FFFC7C", "TBC": "#2c2F33", "TSC": "#DDDB6B", "BC": "#23272A", "TC":"#FFFFFF"}

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

        # instanitate the currentTasks list
        self.TEXT_WRAP_LENGTH = 400
        self.currentTasks = list()
        self.currentButtons = dict()
        self.refreshInUse = False
        self.noColorMode = True

        self.selected = list()
        self.undoList = list()
        self.redoList = list()

        # Create the master frame, task frame, and task entry
        self.masterFrame = Frame(self.display)
        self.masterFrame.pack(fill=BOTH, expand=1)        

        # self.taskFrame = Frame(self.masterFrame, background="royal blue")
        self.taskFrame = Frame(self.masterFrame, background=BACKGROUND_COLOR)
        self.taskEntry = Entry(self.masterFrame, font="SegoeUI 13", background="white")

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
        self.popup_menu.add_command(label="Add/Remove Accent", command=lambda: self.addRemoveAccent())

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

    def getAccentColor(self):
        """
        Return the Windows 10 accent color used by the user in a HEX format
        """
        #Open the registry
        registry = ConnectRegistry(None,HKEY_CURRENT_USER)
        #Navigate to the key that contains the accent color info
        key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent')
        #Read the value in a REG_DWORD format
        key_value = QueryValueEx(key,'StartColorMenu')
        #Convert the interger to Hex and remove its offset
        accent_int = key_value[0]
        accent_hex = hex(accent_int)
        accent_hex = str(accent_hex)[4:10]
        #The HEX value was originally in a BGR order, instead of RGB,
        #so we reverse it...
        accent = accent_hex[4:6]+accent_hex[2:4]+accent_hex[0:2]
        return '#'+accent

    def addRemoveAccent(self):
        """
        Either gets and adds the accent Color, or Removes it
        """
        global ACCENT_COLOR_ON
        global BACKGROUND_COLOR
        if(ACCENT_COLOR_ON):
            global DARK_MODE_ON
            if(DARK_MODE_ON):
                global Dark_Color_Dictionary
                BACKGROUND_COLOR = Dark_Color_Dictionary["BC"]
            else:
                global Main_Color_Dictionary
                BACKGROUND_COLOR = Main_Color_Dictionary["BC"]
            ACCENT_COLOR_ON = False
        else:
            BACKGROUND_COLOR = self.getAccentColor()
            ACCENT_COLOR_ON = True
        self.taskFrame.config(background=BACKGROUND_COLOR)
        

    def onClose(self):
        """
        Run's on attempt to close the application
        """
        if messagebox.askokcancel("Quit", "Do you want to close Pan-Do?"):
            self.display.destroy()

    def changeColorScheme(self):
        print("change color scheme")
        global DARK_MODE_ON
        global CHECK_FILL_COLOR
        global CHECK_OUTLINE_COLOR
        global CHECK_HOVER_FILL_COLOR
        global CHECK_HOVER_OUTLINE_COLOR
        global TASK_BACKGROUND_COLOR
        global TASK_SELECTED_COLOR
        global BACKGROUND_COLOR
        global TEXT_COLOR
        if(DARK_MODE_ON):
            global Main_Color_Dictionary
            CHECK_FILL_COLOR = Main_Color_Dictionary["CFC"]
            CHECK_OUTLINE_COLOR = Main_Color_Dictionary["COC"]
            CHECK_HOVER_FILL_COLOR = Main_Color_Dictionary["CHFC"]
            CHECK_HOVER_OUTLINE_COLOR = Main_Color_Dictionary["CHOC"]
            TASK_BACKGROUND_COLOR = Main_Color_Dictionary["TBC"]
            TASK_SELECTED_COLOR = Main_Color_Dictionary["TSC"]
            BACKGROUND_COLOR = Main_Color_Dictionary["BC"]
            TEXT_COLOR = Main_Color_Dictionary["TC"]
            DARK_MODE_ON = False
            self.noColorMode = True
            self.popup_menu.delete("Light Mode")
        else:
            global Dark_Color_Dictionary
            CHECK_FILL_COLOR = Dark_Color_Dictionary["CFC"]
            CHECK_OUTLINE_COLOR = Dark_Color_Dictionary["COC"]
            CHECK_HOVER_FILL_COLOR = Dark_Color_Dictionary["CHFC"]
            CHECK_HOVER_OUTLINE_COLOR = Dark_Color_Dictionary["CHOC"]
            TASK_BACKGROUND_COLOR = Dark_Color_Dictionary["TBC"]
            TASK_SELECTED_COLOR = Dark_Color_Dictionary["TSC"]
            BACKGROUND_COLOR = Dark_Color_Dictionary["BC"]
            TEXT_COLOR = Dark_Color_Dictionary["TC"]
            DARK_MODE_ON = True
            self.noColorMode = True
            self.popup_menu.delete("Dark Mode")
        self.updateDisplay()


    def updateDisplay(self):
        global BACKGROUND_COLOR
        self.taskFrame.config(background=BACKGROUND_COLOR)
        for task in self.currentTasks:
            self.currentButtons[task].changeColors()

    
    
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
        # print("adding list of tasks")
        # add tasks to the list of current tasks

        oldTasks = list()
        newTasks = list()

        listOfTasks.reverse() # add new from the top
        # print(listOfTasks)
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

        # print(self.currentTasks)

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
        # print("adding task")
        taskText = self.taskEntry.get()
        self.taskEntry.delete(0, END)

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
        # print("refreshing Display")

        y = TASK_DIFF
        for task in self.currentTasks:
            if task not in self.currentButtons:
                # print(task, "button creation")
                
                chk = TaskCanvas(self.display, self.taskFrame, task, self.moveTask,
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
            self.display.configure()
            # print(button.winfo_height(), task)
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

    def setTaskMovedListener(self, listener):
        """
            sets the taskMovedListener function pointer

            Parameter:
            listener -- the function that taskMovedListener is to be set to
        """
        self.taskMovedListener = listener

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

    def makeTrayIcon(self):
        """
        Minimizes to tray icon
        """
        def show(sysTrayIcon): show(self)
        menu_options = (('Open', None , show),)
        def bye(sysTrayIcon): self.close()
        SysTrayIcon("PandoIcon.ico", "Pando", menu_options, on_quit=bye, default_menu_index=1)

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
        # print("currentTasks: " + str(self.currentTasks))
        self.undoList.append(["remove", tasksAdded])
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
        # print("update wrap length")
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
            # print("nothing to undo")
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
            # print("undo add tasks: ",tasks)
            for task in tasks:
                chk = self.currentButtons[task]
                chk.destroy()
                del self.currentButtons[task]
                self.currentTasks.remove(task)

            self.refreshDisplay() # refresh display before notify call
            self.redoList.append(["add", tasks])
            self.remove.notify(tasks)

        elif (action == "edit"):
            edits = undoAction[1] # edit is a list of two elements: old and new
            old = edits[0]
            new = edits[1]

            button = self.currentButtons.get(old)
            button.changeTask(new)
            self.editUpdate(old, new)
            self.editListener.notify([old, new])
            self.redoList.append(["edit", [new, old]])
            # print("redo list: " + str(self.redoList))
            # print("undo list: " + str(self.undoList))
        
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
            # print("nothing to redo")
            return

        redoAction = self.redoList.pop()
        action = redoAction[0]
        if(action == "add"):
            tasks = redoAction[1]

            for task in tasks:
                if (self.currentTasks.count(event) == 0):
                    self.currentTasks.insert(0, task)

            self.refreshDisplay()

            self.undoList.append(["remove", tasks])
            self.add.notify(tasks)
        
        elif (action == "remove"):
            tasks = redoAction[1] # tasks is a list of tasks that need to be removed
            print("undo add tasks: ",tasks)
            for task in tasks:
                chk = self.currentButtons[task]
                chk.destroy()
                del self.currentButtons[task]
                self.currentTasks.remove(task)

            self.refreshDisplay() # refresh display before notify call
            self.undoList.append(["add", tasks])
            self.remove.notify(tasks)

        elif (action == "edit"):
            edits = redoAction[1] # edit is a list of two elements: old and new
            old = edits[0]
            new = edits[1]

            button = self.currentButtons.get(old)
            button.changeTask(new)
            self.editUpdate(old, new)
            self.editListener.notify([old, new])
            self.undoList.append(["edit", [new, old]])
            # print("redo list: " + str(self.redoList))
            # print("undo list: " + str(self.undoList))

        elif (action == "projectSwap"):
            project = redoAction[1]
            for task in self.currentTasks:
                button = self.currentButtons[task]
                button.destroy()
                del self.currentButtons[task]

            self.swapProjectListener.notify(project)
            self.addUndo(["projectSwap", [self.currentProject]])
            self.setCurrentProject(project[0])

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

        # print("drop calculation")
        oldPos = self.currentTasks.index(dragTask)
        newPos = 0
        found = False
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
                    found = True
                    break
                elif (newPos == (listLen - 1)) and (dragMid >= bottom):
                    # print(task, newPos)
                    self.currentTasks.insert(newPos, self.currentTasks.pop(oldPos))
                    found = True
                    break
        
        if (not found):
            newPos = oldPos
            self.refreshDisplay()
        else:
            self.refreshDisplay()
            start_loc = oldPos
            end_loc = newPos
            # sprint("old and new Pos:", oldPos, newPos)
            # self.taskMovedListener.notify([start_loc, end_loc])

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

        self.selected = list()
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
        global DARK_MODE_ON
        self.submenu = Menu(self.popup_menu, tearoff = False)
        
        if(DARK_MODE_ON and self.noColorMode):
            self.noColorMode = False
            self.popup_menu.add_command(label="Light Mode", command=lambda: self.changeColorScheme())
        elif (not DARK_MODE_ON and self.noColorMode):
            self.noColorMode = False
            self.popup_menu.add_command(label="Dark Mode", command=lambda: self.changeColorScheme())

        self.getProjectNames.notify([0])
        # print(self.projectNames, "current project: ", self.currentProject)
        for project in self.projectNames:
            if (project != self.currentProject):
                self.submenu.add_command(label=project,
                                         command=lambda p=project: self.swapProject(p.strip()))

        self.popup_menu.add_cascade(label="swap project",menu=self.submenu)
        
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            print(DARK_MODE_ON)
            # if (DARK_MODE_ON):
            #     self.popup_menu.delete("Light Mode")
            # else:
            #     self.popup_menu.delete("Dark Mode")
            print("getting rid of swap project")
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
        self.initialYPosition = self.winfo_y()
        self.drag_start_y = event.y
        # self.selected(event)
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

class TaskCanvas(DragDropWidget, Canvas):
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
        global TASK_BACKGROUND_COLOR
        DragDropWidget.__init__(self)
        # Frame.__init__(self, parent, background="white")
        Canvas.__init__(self, parent, height=42, highlightthickness=0, background=TASK_BACKGROUND_COLOR)
        self.complete = complete
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
        self.taskStrVar = StringVar(value=task)
        self.entryStrVar = StringVar(value=task)
        self.wrapLengthRefresh = 0
        self.WrapLength = 0
        self.isSelected = False
        self.firstDisplay = True

        self.chk = self.drawCheckOff(21, 21, 10)
        self.line = self.drawLine(40, 350)
        # # self.chk = Checkbutton(self, variable=self.chkVar, command=lambda t = task: complete(t))
        self.taskEntryFrame = Frame(self)
        self.label = Label(self.taskEntryFrame, background="#D3D3D3", textvariable=self.taskStrVar, font="SegoeUI 13", wraplength = textWrapLength, justify=LEFT)
        self.editEntry = Entry(self.taskEntryFrame, font="SegoeUI 13", textvariable=self.entryStrVar)
        self.editEntry.bind('<Return>', lambda e: self.taskMode())

        # # self.chk.pack(side=LEFT)
        self.frameID = self.create_window(42, 21, window = self.taskEntryFrame, anchor = W)
        self.label.pack(side=LEFT)

        self.popup_menu = Menu(self, tearoff=False)
        self.popup_menu.add_command(label="complete", command=lambda t = task: complete(t))
        self.popup_menu.add_command(label="edit", command=lambda: self.editMode())
        
        # drag drop binding on frame
        self.bind("<Button-1>", self.completeTask)
        self.bind("<B1-Motion>", self.drag_motion)
        self.bind("<ButtonRelease-1>", self.drop)    

        # selection binding on frame
        self.bind("<Double-Button-1>", self.completeTask)
        self.bind("<Control-Button-1>", lambda e: self.controlSelect(self.taskStrVar.get()))
        self.bind("<Shift-Button-1>", lambda e: self.shiftSelect(self.taskStrVar.get()))
        
        # drag drop binding on label
        self.label.bind("<Button-1>", self.drag_start)
        self.label.bind("<B1-Motion>", self.drag_motion)
        self.label.bind("<ButtonRelease-1>", self.drop)        

        # selection binding on label
        self.label.bind("<Double-Button-1>", self.selected)
        self.label.bind("<Control-Button-1>", lambda e: self.controlSelect(self.taskStrVar.get()))
        self.label.bind("<Shift-Button-1>", lambda e: self.shiftSelect(self.taskStrVar.get()))
        
        # right click context menu binding on label
        self.label.bind("<Button-3>", self.popup) # windows
        # self.label.bind("<Button-2>", self.popup) # mac

    def drawCheckOff(self, x, y, r):
        global CHECK_FILL_COLOR
        global CHECK_OUTLINE_COLOR
        global CHECK_HOVER_FILL_COLOR
        global CHECK_HOVER_OUTLINE_COLOR
        checkOffID = self.create_oval(x-r, y-r, x+r, y+r, fill=CHECK_FILL_COLOR, outline=CHECK_OUTLINE_COLOR,
                                                          width=2, activewidth=3, activefill=CHECK_HOVER_FILL_COLOR,
                                                          activeoutline=CHECK_HOVER_OUTLINE_COLOR)
        return checkOffID
    
    def drawLine(self, y, length):
        lineID = self.create_line(10, y, 10+length, y, width=2)

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

    def completeTask(self, event):
        xDis = event.x - 21
        yDis = event.y - 21
        xSquare = xDis * xDis 
        ySquare = yDis * yDis
        if math.sqrt(xSquare + ySquare) <= 10:
            self.itemconfig(self.chk, fill = "#E84D00")
            self.complete(self.taskStrVar.get())
        else:
            self.selected(event)

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
        self.taskStrVar.set(newText)
        self.configure()

    def taskMode(self):
        """
        Updates the task with edited text and 
        returns the TaskButton to taskMode
        """
        # print("task mode")
        old = self.getTaskText()
        new = self.entryStrVar.get()
        self.changeTask(new)
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
        global TASK_SELECTED_COLOR
        self.configure(background=TASK_SELECTED_COLOR)
        self.label.configure(background=TASK_SELECTED_COLOR)

    def deSelect(self):
        """
        highlights the TaskButton in white
        """
        global TASK_BACKGROUND_COLOR
        self.configure(background=TASK_BACKGROUND_COLOR)
        self.label.configure(background=TASK_BACKGROUND_COLOR)

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

        self.drag_start(event)

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
    
    def changeColors(self):
        self.itemconfig(self.chk, fill=CHECK_FILL_COLOR)
        self.itemconfig(self.chk, outline=CHECK_OUTLINE_COLOR)
        self.itemconfig(self.chk, activefill=CHECK_HOVER_FILL_COLOR)
        self.itemconfig(self.chk, activeoutline=CHECK_HOVER_OUTLINE_COLOR)
        self.config(background=TASK_BACKGROUND_COLOR)
        self.label.config(background=TASK_BACKGROUND_COLOR)
        self.label.config(foreground=TEXT_COLOR)

class SysTrayIcon(object):
    '''TODO'''
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]
    
    FIRST_ID = 1023
    
    def __init__(self,
                icon,
                hover_text,
                menu_options,
                on_quit=None,
                default_menu_index=None,
                window_class_name=None,):
        
        self.icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit
        
        menu_options = menu_options + (('Quit', None, self.QUIT),)
        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options))
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id
        
        
        self.default_menu_index = (default_menu_index or 0)
        self.window_class_name = window_class_name or "SysTrayIconPy"
        
        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): self.restart,
                    win32con.WM_DESTROY: self.destroy,
                    win32con.WM_COMMAND: self.command,
                    win32con.WM_USER+20 : self.notify,}
        # Register the Window class.
        window_class = win32gui.WNDCLASS()
        hinst = window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = self.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(window_class)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(classAtom,
                                        self.window_class_name,
                                        style,
                                        0,
                                        0,
                                        win32con.CW_USEDEFAULT,
                                        win32con.CW_USEDEFAULT,
                                        0,
                                        0,
                                        hinst,
                                        None)
        win32gui.UpdateWindow(self.hwnd)
        self.notify_id = None
        self.refresh_icon()
        
        win32gui.PumpMessages()

    def _add_ids_to_menu_options(self, menu_options):
        result = []
        for menu_option in menu_options:
            option_text, option_icon, option_action = menu_option
            if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, option_action))
                result.append(menu_option + (self._next_action_id,))
            elif non_string_iterable(option_action):
                result.append((option_text,
                            option_icon,
                            self._add_ids_to_menu_options(option_action),
                            self._next_action_id))
            else:
                print('Unknown item', option_text, option_icon, option_action)
            self._next_action_id += 1
        return result
        
    def refresh_icon(self):
        # Try and find a custom icon
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(self.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst,
                                    self.icon,
                                    win32con.IMAGE_ICON,
                                    0,
                                    0,
                                    icon_flags)
        else:
            print("Can't find icon file - using default.")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        if self.notify_id: message = win32gui.NIM_MODIFY
        else: message = win32gui.NIM_ADD
        self.notify_id = (self.hwnd,
                        0,
                        win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                        win32con.WM_USER+20,
                        hicon,
                        self.hover_text)
        win32gui.Shell_NotifyIcon(message, self.notify_id)

    def restart(self, hwnd, msg, wparam, lparam):
        self.refresh_icon()

    def destroy(self, hwnd, msg, wparam, lparam):
        if self.on_quit: self.on_quit(self)
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0) # Terminate the app.

    def notify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONDBLCLK:
            self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
        elif lparam==win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam==win32con.WM_LBUTTONUP:
            pass
        return True
        
    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)
        #win32gui.SetMenuDefaultItem(menu, 1000, 0)
        
        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                self.hwnd,
                                None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
    
    def create_menu(self, menu, menu_options):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)
            
            if option_id in self.menu_actions_by_id:                
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                                hbmpItem=option_icon,
                                                                hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(self, icon):
        # First load the icon.
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hdcScreen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        # Fill the background.
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
        # unclear if brush needs to be feed.  Best clue I can find is:
        # "GetSysColorBrush returns a cached brush instead of allocating a new
        # one." - implies no DeleteObject
        # draw the icon
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)
        
        return hbm

    def command(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)
        
    def execute_menu_option(self, id):
        menu_action = self.menu_actions_by_id[id]      
        if menu_action == self.QUIT:
            win32gui.DestroyWindow(self.hwnd)
        else:
            menu_action(self)
            
def non_string_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return False
