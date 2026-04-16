import tkinter as tk
from tkinter import ttk

def monitering_gui():
    initial_root = tk.Tk()
    initial_root.geometry('500x350')
    #initial_root.resizable(width=False, height=False)
    initial_root.title("Moniter Patient")
    root = tk.Frame(initial_root)
    root.pack(padx=10, pady=10)
    root.mainloop()

if __name__ == "__main__":
    monitering_gui()