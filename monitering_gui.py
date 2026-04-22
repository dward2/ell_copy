import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import requests
import os

# connect to server
server = "http://67.159.79.173:5000"


def get_apnea_color(a):
    """
    Determine the display color for an apnea value.

    Args:
        a: A value representing apnea severity.
        Expected to be convertible to int.

    Returns:
        str: 'red' if the integer value of `a` is greater than 2,
             otherwise 'black'. Returns 'black' if conversion fails.
    """
    try:
        if int(a) >= 2:
            return 'red'
        else:
            return 'black'
    except (ValueError, TypeError):
        return 'black'


def monitering_gui():
    """
    Launch and manage the patient monitoring GUI.

    This function initializes a Tkinter-based interface for:
    - Selecting hospital rooms
    - Viewing patient information (name, MRN, pressure, breathing rate)
    - Displaying apnea values with color indication
    - Viewing and saving CPAP images
    - Submitting new pressure readings
    - Periodically refreshing patient and room data from a server

    The GUI communicates with a backend server via HTTP requests
    to retrieve and update patient data.

    Internal state is maintained for:
    - Current patient data
    - Selected room and time
    - Loaded CPAP images

    Note:
        This function defines multiple nested helper functions to handle
        UI updates, API communication, and event callbacks.
    """

    current_patient = {
        "name": "",
        "mrn": None,
        "pressure": None,
        "br": None,
        "apnea": None,
        "times": []
    }
    current_img1 = None
    current_img2 = None

    def set_option_menu(menu_widget, variable, options):
        """
        Update a Tkinter OptionMenu with new selectable options.

        Args:
            menu_widget: The OptionMenu widget to update.
            variable: The associated Tkinter variable controlling selection.
            options (iterable): New options to populate the menu.

        Behavior:
            - Clears existing menu entries
            - Adds a default placeholder option "-"
            - Populates menu with provided options
            - Preserves the current selection if still valid,
              otherwise resets to "-"
        """

        current = variable.get()

        menu = menu_widget["menu"]
        menu.delete(0, "end")

        # always include placeholder
        all_options = ["-"] + list(options)

        for opt in all_options:
            menu.add_command(
                label=str(opt),
                command=lambda value=opt: variable.set(value)
            )

        # preserve selection logic
        if current in all_options:
            variable.set(current)
        else:
            variable.set("-")

    def append_new_pressure():
        """
        Send a new pressure reading to the server.

        Reads the value from the input field, sends it via POST request,
        and updates the UI based on success or failure.

        Behavior:
            - On success: clears input and removes warning message
            - On failure: displays validation error message
        """

        # append data to patient
        p = new_pressure.get()
        r = requests.post(server + f"/pressure",
                          json={"room": chosen_room.get(), "pressure": int(p)})
        if r.status_code == 200:
            new_pressure.set("")
            pressure_warning.config(text='')
        else:
            pressure_warning.config(text='Enter integer between 4 and 25')

    def update_rooms():
        """
        Fetch and update the list of available rooms from the server.

        On success:
            - Updates the room selection dropdown menu
        """

        r = requests.get(server + "/rooms")
        if r.status_code == 200:
            new_rooms = r.json()
            set_option_menu(room_select, chosen_room, new_rooms)

    def time_recent():
        """
        Update the most recent CPAP image timestamp.

        Sets the latest time from the current patient's time list
        to the secondary image display. Defaults to "-" if no data exists.
        """

        global current_patient
        try:
            latest = current_patient["times"][-1]
            image2_time.set(latest)
        except IndexError:
            image2_time.set("-")

    def display_patient():
        """
        Retrieve and display patient data for the selected room.

        Fetches patient information from the server and updates:
            - Patient details (name, MRN, pressure, breathing rate)
            - Apnea value and its display color
            - Most recent CPAP image time
        """
        global current_patient
        room_selected = chosen_room.get()
        r = requests.get(server + f"/patient/{room_selected}")
        current_patient = r.json()
        if current_patient.get('times') is None:
            current_patient['times'] = []

        p_data.set(
            f"{current_patient.get('name') or '-'}\n"
            f"id: {current_patient.get('mrn') or '-'}\n"
            f"Latest Pressure: {current_patient.get('pressure') or '-'}\n"
            f"Breathing Rate: {current_patient.get('br') or '-'}"
        )
        apnea_val = current_patient.get("apnea")
        if apnea_val is not None:
            a_data.set(apnea_val)
        else:
            a_data.set('-')

        color = get_apnea_color(a_data.get())
        apnea_data.config(fg=color)

        time_recent()

    def change_times():
        """
        Update the time selection menu based on the current patient.

        Populates the dropdown with available CPAP timestamps.
        """
        global current_patient
        new_times = current_patient.get("times", [])
        set_option_menu(time_select, chosen_time, new_times)

    def clear_image1():
        """
        Clear the primary CPAP image display.

        Resets the image widget and internal image reference.
        """
        global current_img1
        cpap_image1.config(image="", text="Choose a Time")
        cpap_image1.image = None
        current_img1 = None

    def display_image1():
        """
        Display a CPAP image for the selected time.

        Fetches the image from the server based on selected room and time,
        resizes it, and updates the GUI.

        If no valid time is selected, clears the image display.
        """
        global current_img1
        # call when new time is selected
        if chosen_time.get() == "-":
            clear_image1()
        else:
            # find new image file for patient + room
            r = requests.get(server + "/cpap",
                             params={"room": chosen_room.get(),
                                     "time": chosen_time.get()})
            if r.status_code == 200:
                filename = r.text
                with Image.open(filename) as img:
                    pil_img = img.copy()
                img_resized = pil_img.resize((200, 200))
                img_tk = ImageTk.PhotoImage(img_resized)
                cpap_image1.config(image=img_tk, text="")
                cpap_image1.image = img_tk
                current_img1 = pil_img
                os.remove(filename)

    def clear_image2():
        """
        Clear the secondary (most recent) CPAP image display.

        Resets the image widget and internal image reference.
        """
        global current_img2
        cpap_image2.config(image="", text="No recent CPAP")
        cpap_image2.image = None
        current_img2 = None

    def display_image2():
        """
        Display the most recent CPAP image for the selected room.

        Fetches the latest image from the server and updates the GUI.
        Clears the display if no image is available.
        """
        global current_img2
        # call when new room is selected
        if image2_time.get() == "-":
            clear_image2()
        else:
            # find new image file for patient + room
            r = requests.get(server + "/cpap",
                             params={"room": chosen_room.get(),
                                     "time": image2_time.get()})
            if r.status_code == 200:
                filename = r.text
                with Image.open(filename) as img:
                    pil_img = img.copy()
                img_resized = pil_img.resize((200, 200))
                img_tk = ImageTk.PhotoImage(img_resized)
                cpap_image2.config(image=img_tk, text="")
                cpap_image2.image = img_tk
                current_img2 = pil_img
                os.remove(filename)
            else:
                clear_image2()

    def room_changed(*args):
        """
        Handle changes to the selected room.

        Behavior:
            - If no room selected ("-"): resets UI elements
            - Otherwise:
                - Loads patient data
                - Updates available times
                - Displays the most recent CPAP image
        """

        if chosen_room.get() == "-":
            clear_image1()
            clear_image2()
            a_data.set('-')
            p_data.set("Select a room to see a patient's information")
            return
        display_patient()
        change_times()
        display_image2()

    def time_changed(*args):
        """
        Handle changes to the selected time.

        Updates the displayed timestamp and loads the corresponding CPAP image.
        """
        image1_time.set(chosen_time.get())
        display_image1()

    def save_file1():
        """
        Save the currently displayed primary CPAP image to a file.

        Opens a file dialog for the user to choose a save location.
        Does nothing if no image is loaded.
        """
        global current_img1
        if current_img1 is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
        )
        if file_path:
            current_img1.save(file_path)

    def save_file2():
        """
        Save the currently displayed secondary CPAP image to a file.

        Opens a file dialog for the user to choose a save location.
        Does nothing if no image is loaded.
        """
        global current_img2
        if current_img2 is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
        )
        if file_path:
            current_img2.save(file_path)

    def update_data():
        """
        Periodically refresh room and patient data.

        Behavior:
            - Updates room list
            - Refreshes patient data if a room is selected
            - Reschedules itself to run every 10 seconds
        """
        global current_patient
        update_rooms()
        if chosen_room.get() != "-":
            display_patient()
            change_times()

        root.after(10000, update_data)

    initial_root = tk.Tk()
    initial_root.geometry('470x490')
    # initial_root.resizable(width=False, height=False)
    initial_root.title("Moniter Patient")
    root = tk.Frame(initial_root)
    root.pack(padx=10, pady=10)

    room_label = tk.Label(root, text="Select Room Number: ")
    room_label.grid(row=0, column=0, sticky='w')

    chosen_room = tk.StringVar(value="-")
    chosen_room.trace_add("write", room_changed)
    room_select = tk.OptionMenu(root, chosen_room, '-')
    room_select.config(width=10)
    room_select.grid(row=1, column=0, sticky='w')

    patient_label = tk.Label(root, text="Patient: ")
    patient_label.grid(row=0, column=2, sticky='nw')

    p_data = tk.StringVar(value="Select a room to see a patient's information")
    patient_data = tk.Label(root, textvariable=p_data,
                            wraplength=150, justify='left')
    patient_data.grid(column=3, row=0, rowspan=2, sticky='nw')

    time_label = tk.Label(root, text='Select Time:')
    time_label.grid(row=2, column=0, sticky='w')

    root.rowconfigure(4, pad=20)
    chosen_time = tk.StringVar(value="-")
    chosen_time.trace_add("write", time_changed)
    time_select = tk.OptionMenu(root, chosen_time, '-')
    time_select.config(width=10)
    time_select.grid(row=3, column=0, sticky='w')

    apnea_label = tk.Label(root, text="Apnea: ")
    apnea_label.grid(row=3, column=2, sticky='w')

    a_data = tk.StringVar(value='-')
    apnea_color = tk.StringVar()
    apnea_color.set("black")
    apnea_data = tk.Label(root, textvariable=a_data, fg=apnea_color.get())
    apnea_data.grid(column=3, row=3, sticky='wn')

    pressure_label = tk.Label(root, text='New Pressure Reading: ')
    pressure_label.grid(row=4, column=0, sticky='e')

    def validate_int(P):
        """
        Blocks any input to the pressure entry that is non-numeric

        Args:
            P (str): Proposed new value of the input field.

        Returns:
            bool: True if input is digits or empty, False otherwise.
        """
        return P.isdigit() or P == ""
    vcmd = (root.register(validate_int), "%P")

    new_pressure = tk.StringVar()
    pressure_entry = tk.Entry(
        root,
        textvariable=new_pressure,
        validate="key",
        validatecommand=vcmd,
        width=8
    )
    pressure_entry.grid(row=4, column=1, sticky='w')

    root.rowconfigure(5, pad=10)
    pressure_button = tk.Button(root, text='Submit',
                                command=append_new_pressure)
    pressure_button.grid(row=5, column=1, sticky='n')

    pressure_warning = tk.Label(root, text="",
                                font=("Helvetica", 10, "italic"))
    pressure_warning.grid(row=4, column=2, columnspan=2, sticky='w')

    # images
    cpap_image1 = tk.Label(root, text="Choose a Time",
                           font=("Helvetica", 10, "italic"))
    cpap_image1.grid(row=6, column=0, columnspan=2, sticky='s')

    cpap_image2 = tk.Label(root, text="No recent CPAP",
                           font=("Helvetica", 10, "italic"))
    cpap_image2.grid(row=6, column=2, columnspan=2, sticky='s')

    image1_time = tk.StringVar()
    image1_time.set(chosen_time.get())
    image1_label = tk.Label(root, textvariable=image1_time)
    image1_label.grid(row=7, column=0, columnspan=2)

    recent_time = "-"
    image2_time = tk.StringVar()
    image2_time.set(recent_time)
    image2_label = tk.Label(root, textvariable=image2_time)
    image2_label.grid(row=7, column=2, columnspan=2)

    save_image1 = tk.Button(root, text='Save Image', command=save_file1)
    save_image1 .grid(row=8, column=0, columnspan=2)
    save_image2 = tk.Button(root, text='Save Image', command=save_file2)
    save_image2.grid(row=8, column=2, columnspan=2)

    update_data()
    root.mainloop()


if __name__ == "__main__":
    monitering_gui()
