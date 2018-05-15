from tkinter import *
# from tkinter.ttk import *
from listeners import Listener

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
        DragDropWidget.__init__(self)
        # Frame.__init__(self, parent, background="white")
        Canvas.__init__(self, parent, height=42, highlightthickness=0, background="#D3D3D3")
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

        self.drawCheckOff(21, 21, 10, "red")

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
        self.bind("<Button-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag_motion)
        self.bind("<ButtonRelease-1>", self.drop)    

        # selection binding on frame
        self.bind("<Double-Button-1>", self.selected)
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

    def drawCheckOff(self, x, y, r, color):
        checkOffID = self.create_oval(x-r, y-r, x+r, y+r, fill="#FFFFFF", outline="#E84D00", width=2, activewidth=3, activefill="#E84D00", activeoutline="#FFFC7C")
        return checkOffID

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
        self.configure(background="#FFFC7C")
        self.label.configure(background="#FFFC7C")

    def deSelect(self):
        """
        highlights the TaskButton in white
        """
        self.configure(background="#D3D3D3")
        self.label.configure(background="#D3D3D3")

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

def helloWorld(item):
    print("hello World")

root = Tk()
l = Listener(helloWorld)
canvasButton = TaskCanvas(root, root, "Hello World", l,400,l,l,l,l,l,l,l,l,l)
canvasButton.place(x=0, y=0, relwidth=1.0)

root.mainloop()
