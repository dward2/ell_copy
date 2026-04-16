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

mrn_value = tk.StringVar()
mrn_entry = tk.Entry(root, font=base_font,
                     textvariable=mrn_value, width=18)
mrn_entry.grid(column=2, row=3, sticky=tk.E, padx=5)
mrn_label = tk.Label(root, text="Medical Record Number",
                     font=base_font)
mrn_label.grid(column=2, row=1, sticky=tk.W, padx=5)

rn_value = tk.StringVar()
rn_entry = tk.Entry(root, font=base_font,
                    textvariable=rn_value, width=11)
rn_entry.grid(column=3, row=3, sticky=tk.E, padx=5)
rn_label = tk.Label(root, text="Room Number", font=base_font)
rn_label.grid(column=3, row=1, sticky=tk.W, padx=5)

root.mainloop()
