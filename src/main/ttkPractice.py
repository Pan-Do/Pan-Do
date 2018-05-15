from tkinter import *
from tkinter.ttk import *
 
FONT_GENERAL = ("Sogeo UI", 50)

window = Tk()

window.title("Pan-Do")
 
window.geometry('350x500')
 
combo = Combobox(window)
 
combo['values']= (1, 2, 3, 4, 5, "Text")
 
combo.current(1) #set the selected item
 
combo.grid(column=0, row=0)

lbl = Label(window, text="This is a text", font=FONT_GENERAL)
 
lbl.grid(column=0, row=1)
 
window.mainloop()