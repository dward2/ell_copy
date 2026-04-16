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

    patient_label = tk.Label(root, text="Patient: ")
    patient_label.grid(row=0, column=2, sticky='e')

    p_data = tk.StringVar(value='Ella Fortenbery, id: 123')
    patient_data = tk.Label(root, textvariable=p_data)
    patient_data.grid(column=3, row=0, sticky='w')
    
    time_label = tk.Label(root, text='Select Time:')
    time_label.grid(row=1, column=0, sticky='e')

    chosen_time = tk.StringVar(value="-")
    times = ['00:30', '08:17', '14:45']
    time_select = tk.OptionMenu(root, chosen_time, *times)
    time_select.grid(row=1, column=1, sticky='w')
    
    apnea_label = tk.Label(root, text="Apnea: ")
    apnea_label.grid(row=1, column=2, sticky='e')

    a_data = tk.IntVar(value='1')
    apnea_color = tk.StringVar()
    if a_data.get() > 2:
        apnea_color.set("red")
    else:
        apnea_color.set("black")
    apnea_data = tk.Label(root, textvariable=a_data, fg=apnea_color.get())
    apnea_data.grid(column=3, row=1, sticky='w')
    
    root.mainloop()

if __name__ == "__main__":
    monitering_gui()