import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib as plt

base_font = ("Georgia", 24)
big_font = ("Georgia", 32, "bold")
small_font = ("Georgia", 16)

root = tk.Tk()
root.title("Sleep Lab Monitoring System")
root.resizable(False, False)

name_value = tk.StringVar()
name_entry = tk.Entry(root, font=base_font,
                      textvariable=name_value, width=15)
name_entry.grid(column=0, row=3, padx=5)
name_label = tk.Label(root, text="Patient Name",
                      font=base_font)
name_label.grid(column=0, row=1, sticky=tk.W, padx=5)

root.mainloop()
