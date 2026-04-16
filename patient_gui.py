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


def validate_name(name):
    name = name.strip()
    if len(name) == 0:
        return "Please enter a patient name."
    else:
        for c in name:
            if c.isalpha():
                continue
            elif c == " ":
                continue
            elif c == "-":
                continue
            else:
                return "Name invalid"
        return True


def validate_mrn(mrn):
    mrn = mrn.strip()
    if len(mrn) == 0:
        return "Please enter Medical Record Number"
    if not mrn.isdigit():
        return "MRN Invalid"
    return True


def validate_rn(rn):
    rn = rn.strip()
    if len(rn) == 0:
        return "Please enter Room Number"
    if not rn.isdigit():
        return "Room Number Invalid"
    return True


def validate_pressure(pres):
    pres = pres.strip()
    if len(pres) == 0:
        return True
    if not pres.isdigit():
        return "CPAP pressure must be an integer"
    pres_int = int(pres)
    if pres_int < 4 or pres_int > 25:
        return "CPAP pressure must be between 4 and 25"
    return True


def main_window():

    def name_enter():
        result = validate_name(name_value.get())
        if result is not True:
            status_value.set(result)
            return False
        return True

    def mrn_enter():
        result = validate_mrn(mrn_value.get())
        if result is not True:
            status_value.set(result)
            return False
        return True

    def rn_enter():
        result = validate_rn(rn_value.get())
        if result is not True:
            status_value.set(result)
            return False
        return True

    def pressure_enter():
        result = validate_pressure(cpap_value.get())
        if result is not True:
            status_value.set(result)
            return False
        return True

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

    cpap_value = tk.StringVar()
    cpap_entry = tk.Entry(root, font=base_font,
                          textvariable=rn_value, width=20)
    cpap_entry.grid(column=4, row=3, sticky=tk.E, padx=5)
    cpap_label = tk.Label(root, text="CPAP Pressure (cmH2O)", font=base_font)
    cpap_label.grid(column=4, row=1, sticky=tk.W, padx=5)

    button_file = tk.Button(root, text="Select CPAP File",
                            font=base_font, state=tk.DISABLED)
    button_file.grid(column=0, row=9, sticky=tk.W, padx=10)

    button_reset = tk.Button(root, text="Reset",
                             font=base_font, state=tk.DISABLED)
    button_reset.grid(column=3, row=9, sticky=tk.W, padx=10)

    button_up = tk.Button(root, text="Upload",
                          font=base_font, state=tk.DISABLED)
    button_up.grid(column=2, row=9, sticky=tk.W, padx=10)

    frame = ttk.Frame(root, borderwidth=20, relief=tk.GROOVE)
    frame.grid(column=0, row=6, columnspan=5, pady=10)

    status_value = tk.StringVar(value="Enter Patient Information Above")
    status_label = tk.Label(frame, textvariable=status_value, font=base_font)
    status_label.grid(column=0, row=7, columnspan=5, padx=15)

    # root.mainloop()


if __name__ == "__main__":
    main_window()
