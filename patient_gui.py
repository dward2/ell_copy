import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib as plt

base_font = ("Georgia", 24)
big_font = ("Georgia", 32, "bold")
small_font = ("Georgia", 16)


def validate_name(name):
    '''Validates that a patient name contains letters, spaces,
    or hyphens only.
    Args:
        name (str): The patient name to validate.
    Returns:
        True if the name is valid, or False
        if the name is invalid.
    '''
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
    '''Validates that a medical record number contains only digits.
    Args:
        mrn (str): The medical record number to validate.
    Returns:
        True if the MRN is valid, or False
        if the MRN is empty or contains non-digit characters.
    '''
    mrn = mrn.strip()
    if len(mrn) == 0:
        return "Please enter Medical Record Number"
    if not mrn.isdigit():
        return "MRN Invalid"
    return True


def validate_rn(rn):
    '''Validates that a room number contains only digits.
    Args:
        rn (str): The room number to validate.
    Returns:
        True if the room number is valid, or False
        if the room number is empty or contains
        non-digit characters.
    '''
    rn = rn.strip()
    if len(rn) == 0:
        return "Please enter Room Number"
    if not rn.isdigit():
        return "Room Number Invalid"
    return True


def validate_pressure(pres):
    '''Validates that a CPAP pressure is an integer between 4 and 25.
    An empty entry is considered valid since CPAP pressure is optional.
    Args:
        pres (str): The CPAP pressure value to validate.
    Returns:
        True if the pressure is valid or empty, or False
        if the value is not an integer or is
        outside the range of 4 to 25
    '''
    pres = pres.strip()
    if len(pres) == 0:
        return True
    if not pres.isdigit():
        return "CPAP pressure must be an integer"
    pres_int = int(pres)
    if pres_int < 4 or pres_int > 25:
        return "CPAP pressure must be between 4 and 25"
    return True


def only_digits(value):
    """Validates that the entry contains only digits.
    Allows empty string for when the user deletes all text.
    Args:
        value (str): The proposed value of the entry field.
    Returns:
        bool: True if value is empty or all digits, False otherwise.
    """
    if value == "":
        return True
    return value.isdigit()


def main_window():

    def name_enter():
        '''Validates the patient name entry and update the status
        bar with an error message if validation fails.
        Returns:
            bool: True if the name is valid, False otherwise
        '''
        result = validate_name(name_value.get())
        if result is not True:
            return False
        return True

    def mrn_enter():
        '''Validates the MRN entry and updates the status bar
        with an error message if validation fails.
        Returns:
            bool: True if the MRN is valid, False otherwise.
        '''
        result = validate_mrn(mrn_value.get())
        if result is not True:
            return False
        return True

    def rn_enter():
        '''Validates the room number entry and updates the status
        bar with an error message if validation fails.
        Returns:
            bool: True if the room number is valid, False otherwise.
        '''
        result = validate_rn(rn_value.get())
        if result is not True:
            return False
        return True

    def pressure_enter():
        '''Validates the CPAP pressure entry and updates the status
        bar with an error message if validation fails.
        Returns:
            bool: True if the pressure is valid, False otherwise.
        '''
        result = validate_pressure(cpap_value.get())
        if result is not True:
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
    vcmd = root.register(only_digits)
    mrn_entry = tk.Entry(root, font=base_font,
                         textvariable=mrn_value, width=18,
                         validate="key",
                         validatecommand=(vcmd, "%P"))
    mrn_entry.grid(column=2, row=3, sticky=tk.E, padx=5)
    mrn_label = tk.Label(root, text="Medical Record Number",
                         font=base_font)
    mrn_label.grid(column=2, row=1, sticky=tk.W, padx=5)

    rn_value = tk.StringVar()
    rn_entry = tk.Entry(root, font=base_font,
                        textvariable=rn_value, width=11,
                        validate="key",
                        validatecommand=(vcmd, "%P"))
    rn_entry.grid(column=3, row=3, sticky=tk.E, padx=5)
    rn_label = tk.Label(root, text="Room Number", font=base_font)
    rn_label.grid(column=3, row=1, sticky=tk.W, padx=5)

    cpap_value = tk.StringVar()
    cpap_entry = tk.Entry(root, font=base_font,
                          textvariable=cpap_value, width=20)
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

    root.mainloop()


if __name__ == "__main__":
    main_window()
