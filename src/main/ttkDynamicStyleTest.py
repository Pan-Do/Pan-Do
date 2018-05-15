from tkinter import *
from tkinter.ttk import *
import ttkGui
import listeners

def HelloWorld(item):
    print("Hello world!")

l = listeners.Listener(HelloWorld)

root = Tk()

s = Style()
s.configure('Wild.TFrame', background="royal blue")
s.map('Wild.TFrame', background=[('selected', 'yellow')])

frame = Frame(style='Wild.TFrame', width=400, height=400)
spec = frame.state(('selected', 'true'))
frame.pack()
print(spec)

# tButton = ttkGui.TaskButton(root, root, "New Task", l, 50, l, l, l, l, l, l, l, l, l)
# tButton.place(x=0, y= 0)

root.mainloop()