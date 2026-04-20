import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import requests

# connect to server
server = 'http://127.0.0.1:5000'

def monitering_gui():

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

    def append_new_pressure():
        # append data to patient
        p = new_pressure.get()
        r = requests.post(server + f"/pressure/{p}")
        if r.status_code == 200:
            new_pressure.set("")
            pressure_warning.config(text='')
        else:
            pressure_warning.config(text='Enter integer between 4 and 25')


    def update_rooms():
        menu = room_select["menu"]
        r = requests.get(server+"/rooms")
        if r.status_code == 200:
            new_rooms = r.json()
        for room in new_rooms:
            # only add NEW rooms to the option menu
            if room not in rooms:
                rooms.append(room)
                menu.add_command(
                    label=str(room),
                    command=tk._setit(chosen_room, str(room))
                )


    def add_times():
        menu = time_select["menu"]
        new_times = current_patient["times"]
        for time in new_times:
            # only add NEW times to the option menu
            if time not in times:
                times.append(time)
                menu.add_command(
                    label=str(time),
                    command=tk._setit(chosen_time, str(time))
                )


    def display_patient():
        global current_patient
        try:
            room_selected = int(chosen_room.get())
        except:
            return
        r = requests.get(server + f"/patient/{room_selected}")
        current_patient = r.json()
        print(current_patient.get("times", []))

        p_data.set(f"{current_patient['name']}\nid: {current_patient['mrn']}\nLatest Pressure: {current_patient['pressure']}\nBreathing Rate: {current_patient['br']}")
        a_data.set(int(current_patient["apnea"]))

        if a_data.get() > 2:
            apnea_data.config(fg="red")
        else:
            apnea_data.config(fg="black")


    def change_times():
        global current_patient
        # reset menu and add room's patient's times
        chosen_time.set('-')
        menu = time_select["menu"]
        # delete all times
        menu.delete(0, "end")
        times.clear()
        new_times = current_patient.get("times", [])
        print(new_times)
        for t in new_times:
            menu.add_command(
                label=t,
                command=tk._setit(chosen_time, t)
            )


    def room_changed(*args):
        display_patient()
        change_times()


    def save_file1():
        global current_img1
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
        )
        if file_path:
            current_img1.save(file_path)    


    def save_file2():
        global current_img2
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
        )
        if file_path:
            current_img2.save(file_path)


    def update_data():
        global current_img1
        global current_img2

        update_rooms()
        display_patient()
        add_times()
        current_img1 = img_open1
        current_img2 = img_open2
        root.after(30000, update_data)


    initial_root = tk.Tk()
    initial_root.geometry('470x470')
    # initial_root.resizable(width=False, height=False)
    initial_root.title("Moniter Patient")
    root = tk.Frame(initial_root)
    root.pack(padx=10, pady=10)

    room_label = tk.Label(root, text="Select Room Number: ")
    room_label.grid(row=0, column=0, sticky='w')

    chosen_room = tk.StringVar(value="-")
    chosen_room.trace_add("write", room_changed)
    rooms = ['000']
    room_select = tk.OptionMenu(root, chosen_room, *rooms)
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
    times = ['mm/dd/yy hh:mm', '12/31/99 08:17', '03/05/09 14:45']
    time_select = tk.OptionMenu(root, chosen_time, *times)
    time_select.config(width=10)
    time_select.grid(row=3, column=0, sticky='w')

    apnea_label = tk.Label(root, text="Apnea: ")
    apnea_label.grid(row=3, column=2, sticky='w')

    a_data = tk.IntVar(value='-')
    apnea_color = tk.StringVar()
    apnea_color.set("black")
    apnea_data = tk.Label(root, textvariable=a_data, fg=apnea_color.get())
    apnea_data.grid(column=3, row=3, sticky='wn')

    pressure_label = tk.Label(root, text='New Pressure Reading: ')
    pressure_label.grid(row=4, column=0, sticky='e')

    def validate_int(P):
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

    pressure_warning = tk.Label(root, text="", font=("Helvetica", 10, "italic"))
    pressure_warning.grid(row=4, column=2, columnspan=2, sticky='w')

    # display cpap images:
    img_open1 = Image.open("cpap1.png")
    img_resized1 = img_open1.resize((200, 200))
    img_tk1 = ImageTk.PhotoImage(img_resized1)
    cpap_image1 = tk.Label(root, image=img_tk1)
    cpap_image1.image = img_tk1
    cpap_image1.grid(row=6, column=0, columnspan=2, sticky='s')

    img_open2 = Image.open("cpap2.png")
    img_resized2 = img_open2.resize((200, 200))
    img_tk2 = ImageTk.PhotoImage(img_resized2)
    cpap_image2 = tk.Label(root, image=img_tk2)
    cpap_image2.image = img_tk2
    cpap_image2.grid(row=6, column=2, columnspan=2, sticky='s')

    image1_time = tk.StringVar()
    image1_time.set(chosen_time.get())
    image1_label = tk.Label(root, textvariable=image1_time)
    image1_label.grid(row=7, column=0, columnspan=2)

    recent_time = "Now"
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
