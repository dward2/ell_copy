import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from cpap_analysis import cpap_analysis
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
import requests
import base64

# connect to server
server = 'http://127.0.0.1:5000'

base_font = ("Georgia", 24)
big_font = ("Georgia", 32, "bold")
small_font = ("Georgia", 16)


def validate_name(name):
    '''Validates that a patient name contains letters, spaces,
    or hyphens only.
    Args:
        name (str): The patient name to validate.
    Returns:
        True if the name is valid, or an error message string
        if the name is empty or contains invalid characters.
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
        True if the MRN is valid, or an error message string
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
        True if the room number is valid, or an error message
        string if the room number is empty or contains
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
    True if the pressure is valid or empty, or an error
    message string if the value is not an integer or is
    outside the range of 4 to 25.
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


def check_required_fields(mrn, rn):
    """Checks if required fields are filled
    to clear patient for CPAP file selection,
    returns a list of missing field names.
    Args:
        mrn (str): The medical record number value.
        rn (str): The room number value.
    Returns:
        list: List of missing field names, empty if all
        required fields are filled.
    """
    errors = []
    mrn_result = validate_mrn(mrn)
    if mrn_result is not True:
        errors.append(mrn_result)
    rn_result = validate_rn(rn)
    if rn_result is not True:
        errors.append(rn_result)
    return errors


def apnea_color(ap):
    '''Deterimines the display color for apnea count.
    Red if apnea count is 2 or greater.
    White/default otherwise.
    Args:
        ap (int): The number of apnea events.
    Returns:
        str: 'red' if count >= 2, 'white' otherwise.
    '''
    if ap >= 2:
        return "red"
    else:
        return "white"


def encode_image(image_file):
    image_bytes = image_file.read()
    img_str = base64.b64encode(image_bytes).decode("utf-8")
    return img_str


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

    def check_entry(*args):
        '''Enables or disables the CPAP file selection button.
        Updates the status bar with missing field names
        or a ready message.
        Args:
        *args: Unused arguments passed by trace_add callback.
        '''
        errors = check_required_fields(mrn_value.get(), rn_value.get())
        if errors:
            button_file.config(state=tk.DISABLED)
            button_up.config(state=tk.DISABLED)
            status_value.set("\n".join(errors))
        else:
            button_file.config(state=tk.NORMAL)
            button_up.config(state=tk.NORMAL)
            status_value.set("Ready to select CPAP file.")

    def check_reset(*args):
        '''Enable reset button if any field has data entered.
        Args:
            *args: Unused arguments passed by trace_add callback.
        '''
        if (name_value.get() or mrn_value.get()
                or rn_value.get() or cpap_value.get()):
            button_reset.config(state=tk.NORMAL)
        else:
            button_reset.config(state=tk.DISABLED)

    def select_cpap_file():
        '''Opens file dialog to select and analyze a CPAP data file.
        Displays breathing rate and apnea count in the GUI.
        Apnea count is displayed in red if >= 2.
        '''
        filename = filedialog.askopenfilename(
            title="Select CPAP data file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename == "":
            return
        results = cpap_analysis(filename)
        br_value.set(str(int(results["breathing_rate"])))
        apnea_value.set(str(results["apnea_count"]))
        apnea_display.config(fg=apnea_color(results["apnea_count"]))

        cpap_plot(results["time_data"], results["flow_data"])
        status_value.set("CPAP data analyzed.")

    def cpap_plot(time_data, flow_data):
        """Create and display a flow vs time plot in the GUI.
        Upload plot to server.
        Args:
            time_data (list): time values in seconds.
            flow_data (list): flow rate values.
        """
        for widget in plot_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(time_data, flow_data)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Flow Rate (L/s)")
        ax.set_title("Flow vs Time")

        # upload image to server as bytes
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        image_str.set(encode_image(buf))

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=0)
        plt.close(fig)

    def reset_device():
        '''Resets all fields and displays to their default state.
        Clears all entries, results, and plot.
        Reactivates MRN and room number entries.
        '''
        name_value.set("")
        mrn_value.set("")
        rn_value.set("")
        cpap_value.set("")
        br_value.set("")
        apnea_value.set("")
        image_str.set("")
        apnea_display.config(fg="black")

        for widget in plot_frame.winfo_children():
            widget.destroy()

        mrn_entry.config(state=tk.NORMAL)
        rn_entry.config(state=tk.NORMAL)

        button_file.config(state=tk.DISABLED)
        button_up.config(state=tk.DISABLED)
        button_reset.config(state=tk.DISABLED)

        status_value.set("Enter Patient Information Above")

    def upload():
        '''Uploads patient data to the server,
        Locks MRN and room number after upload.
        Requires MRN and room number and can
        optionally upload CPAP and name data.
        '''
        errors = check_required_fields(
            mrn_value.get(), rn_value.get()
        )
        if errors:
            status_value.set("\n".join(errors))
            return

        data = {
            "mrn": int(mrn_value.get().strip()),
            "room_number": rn_value.get().strip(),
        }

        name = name_value.get().strip()
        if name:
            data["name"] = name

        pres = cpap_value.get().strip()
        br = br_value.get().strip()
        apnea = apnea_value.get().strip()
        if pres and apnea and br:
            data["cpap_pressure"] = int(pres)
            data["breathing_rate"] = int(br_value.get())
            data["apnea_count"] = int(apnea_value.get())
        if image_str.get():
            data["image"] = image_str.get()

        print("Sending data:", data)
        r = requests.post(server + "/api/patient", json=data)
        if r.status_code == 200:
            mrn_entry.config(state=tk.DISABLED)
            rn_entry.config(state=tk.DISABLED)
            status_value.set("Successful Upload.")
        else:
            status_value.set("Upload Failed.")

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
                          textvariable=cpap_value, width=20,
                          validate="key",
                          validatecommand=(vcmd, "%P"))
    cpap_entry.grid(column=4, row=3, sticky=tk.E, padx=5)
    cpap_label = tk.Label(root, text="CPAP Pressure (cmH2O)", font=base_font)
    cpap_label.grid(column=4, row=1, sticky=tk.W, padx=5)

    button_file = tk.Button(root, text="Select CPAP File",
                            font=base_font, state=tk.DISABLED,
                            command=select_cpap_file)
    button_file.grid(column=0, row=9, sticky=tk.W, padx=10)

    button_reset = tk.Button(root, text="Reset",
                             font=base_font, state=tk.DISABLED,
                             command=reset_device)
    button_reset.grid(column=3, row=9, sticky=tk.W, padx=10)

    button_up = tk.Button(root, text="Upload",
                          font=base_font, state=tk.DISABLED,
                          command=upload)
    button_up.grid(column=2, row=9, sticky=tk.W, padx=10)

    br_value = tk.StringVar()
    br_label = tk.Label(root, text="Breathing rate (bpm):",
                        font=base_font)
    br_label.grid(column=0, row=5, sticky=tk.W, padx=5)
    br_display = tk.Label(root, textvariable=br_value,
                          font=base_font)
    br_display.grid(column=1, row=5, sticky=tk.W, padx=5)

    apnea_value = tk.StringVar()
    apnea_label = tk.Label(root, text="Apnea Events:",
                           font=base_font)
    apnea_label.grid(column=2, row=5, sticky=tk.W, padx=5)
    apnea_display = tk.Label(root, textvariable=apnea_value,
                             font=base_font)
    apnea_display.grid(column=3, row=5, sticky=tk.W, padx=5)

    frame = ttk.Frame(root, borderwidth=20, relief=tk.GROOVE)
    frame.grid(column=0, row=6, columnspan=5, pady=10)

    image_str = tk.StringVar()
    plot_frame = tk.Frame(root)
    plot_frame.grid(column=0, row=8, columnspan=5, pady=10)

    status_value = tk.StringVar(value="Enter Patient Information Above")
    status_label = tk.Label(frame, textvariable=status_value, font=base_font)
    status_label.grid(column=0, row=7, columnspan=5, padx=15)

    mrn_value.trace_add("write", check_entry)
    rn_value.trace_add("write", check_entry)

    name_value.trace_add("write", check_reset)
    mrn_value.trace_add("write", check_reset)
    rn_value.trace_add("write", check_reset)
    cpap_value.trace_add("write", check_reset)
    root.mainloop()


if __name__ == "__main__":
    main_window()
