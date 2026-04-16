import tkinter as tk
from tkinter import ttk

def monitering_gui():
    initial_root = tk.Tk()
    initial_root.geometry('500x350')
    #initial_root.resizable(width=False, height=False)
    initial_root.title("Moniter Patient")
    root = tk.Frame(initial_root)
    root.pack(padx=10, pady=10)
    
    room_label = tk.Label(root, text="Select Room Number: ")
    room_label.grid(row=0, column=0, sticky='e')

    chosen_room = tk.StringVar(value="-")
    rooms = [100, 200, 300]
    room_select = tk.OptionMenu(root, chosen_room, *rooms)
    room_select.grid(row=0, column=1, sticky='w')

    
    
    
    root.mainloop()

if __name__ == "__main__":
    monitering_gui()