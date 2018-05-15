from tkinter import *
from listeners import *
import math

class DragDropWidget:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.drag_start_x = 0
        self.drag_start_y = 0

    def drag_start(self, event):
        print("drag start")
        # self.drag_start_x = event.x
        self.drag_start_y = event.y
        print(self.drag_start_y, event.y, self.winfo_height())

    def drag_motion(self, event):        
        # x = self.winfo_x() - self.drag_start_x + event.x
        y = self.winfo_y() - self.drag_start_y + event.y 
        print("drag start: " + str(self.drag_start_y) + " event: " + str(event.y) + " y: " + str(y))
        self.place(x = 0, y = y, relwidth=1.0)

    def drop(self, event):
        wHeight = 40
        wYPosition = self.winfo_y()
        newPosIndex = math.floor((wYPosition / wHeight) + 0.5)
        newPos = newPosIndex * wHeight
        print(newPos, newPosIndex)
        self.place(x = 0, y = newPos, relwidth=1.0)

class TaskButton(DragDropWidget, Frame):

    def __init__(self, window, parent, task, complete, editListener, select, deselect):
        DragDropWidget.__init__(self)
        Frame.__init__(self, parent)
        self.backgroundClr = "white"
        self.root = window
        self.editListener = editListener
        self.parentSelect = select
        self.parentDeselect = deselect

        self.chkVar = IntVar(value=0)
        self.strVar = StringVar(value=task)
        self.configure(background=self.backgroundClr)

        self.chk = Checkbutton(self, variable=self.chkVar, background=self.backgroundClr, command=lambda t = task: complete(t))
        self.label = Label(self, textvariable=self.strVar, font="SegoeUI 15", background=self.backgroundClr)
        self.editEntry = Entry(self, font="SegoeUI 15", background=self.backgroundClr)

        # self.pack(fill=BOTH)
        self.chk.grid(row=0, column=0, padx=10, sticky=W)
        self.label.grid(row=0, column=1, sticky=W)

        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="complete", command=lambda t = task: complete(t))
        self.popup_menu.add_command(label="edit", command=lambda: self.editMode())
        
        self.bind("<Button-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag_motion)
        self.bind("<ButtonRelease-1>", self.drop)
        self.bind("<Double-Button-1>", self.selected) # windows
        # self.label.bind("<Double-Button-2>", self.popup) # mac
        self.editEntry.bind('<Return>', lambda: self.taskMode())
        self.label.bind("<Button-1>", self.drag_start)
        self.label.bind("<B1-Motion>", self.drag_motion)
        self.label.bind("<ButtonRelease-1>", self.drop)
        self.label.bind("<Double-Button-1>", self.selected)
        self.label.bind("<Button-3>", self.popup) # windows
        # self.label.bind("<Button-2>", self.popup) # mac

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def editMode(self):
        print("edit mode")
        self.label.grid_remove()
        self.editEntry.grid(row=0, column=1, sticky=W)
        self.grid()

    def taskMode(self):
        print("task mode")
        old = self.label.cget("text")
        new = self.editEntry.get()
        self.strVar.set(new)
        self.editEntry.delete(0, END)
        self.editEntry.grid_remove()
        self.label.grid()
        self.grid()
        self.editListener.notify([old, new])

    def selected(self, event):
        print("selected")
        self.parentSelect(self.getTaskText())
        self.configure(background="yellow")
        self.label.configure(background="yellow")
        self.chk.configure(background="yellow")
        self.bind("<Double-Button-1>", self.deSelected)
        self.label.bind("<Double-Button-1>", self.deSelected)

    def deSelected(self, event):
        print("deselected")
        self.parentDeselect(self.getTaskText())
        self.configure(background="white")
        self.label.configure(background="white")
        self.chk.configure(background="white")
        self.bind("<Double-Button-1>", self.selected)
        self.label.bind("<Double-Button-1>", self.selected)

    def deSelectAll(self):
        self.configure(background="white")
        self.label.configure(background="white")
        self.chk.configure(background="white")
        self.bind("<Double-Button-1>", self.selected)
        self.label.bind("<Double-Button-1>", self.selected)

    def getTaskText(self):
        return self.label.cget("text")

TASK_HEIGHT = 40

def printHello(foo):
    print(foo)

def displayList(list, window, frame, L):
    y = 0
    for task in list:
        tButton = TaskButton(window, frame, task, L, L, L, L)
        tButton.place(x=0, y = y, relwidth = 1.0)
        print(task, y, tButton.winfo_height())
        y = y + TASK_HEIGHT # TODO: make a constant some time

def displayPlacementSpots(parent):
    y = 0
    while y < 400:
        foo = Frame(parent, height=29, background="black")
        foo.place(x=0,y=y, relwidth=1.0)
        y = y + TASK_HEIGHT

root = Tk()
root.geometry('400x400')
listen = NullListener(printHello)
frame = Frame(root, background="#66ccff")

tasks = ["Hello there!", "General Kenobi!", "I have the high ground!"]
frame.place(x = 0, y = 0, relheight=1.0, relwidth=1.0)
# frame.pack(fill=BOTH)
displayPlacementSpots(frame)
displayList(tasks, root, frame, printHello)

# DragTask00 = TaskButton(root, frame, "Hello, World!", printHello, printHello, printHello, printHello)
# DragTask01 = TaskButton(root, frame, "Hello, World!", printHello, printHello, printHello, printHello)

# DragTask00.place(x = 0, y = 0, relwidth=1.0)
# DragTask01.place(x = 0, y = 0, relwidth=1.0)
root.mainloop()


