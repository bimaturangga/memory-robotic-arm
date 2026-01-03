from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import serial
import time
import threading

port_opened = False
arduino = None
running = True

def set_port():
    global port_opened, arduino
    com_port = port_input.get()
    try:
        arduino = serial.Serial(com_port, 9600, timeout=1)
        time.sleep(2)  # Tunggu Arduino reset
        port_opened = True
        status_label.config(text="Status: Connected to " + com_port, fg="green")
        print("COM port set to: " + com_port)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open port {com_port}\n{str(e)}")
        print(f"Error: {e}")

def send_positions(position):
    if not port_opened:
        return
    
    # Format: 4 servo x 3 digit = 12 karakter + newline
    message = "{0:0=3d}".format(position[0]) + \
              "{0:0=3d}".format(position[1]) + \
              "{0:0=3d}".format(position[2]) + \
              "{0:0=3d}".format(position[3]) + "\n"
    
    try:
        arduino.write(str.encode(message))
    except Exception as e:
        print(f"Error sending data: {e}")

saved_positions = []

def save_positions():
    position = [servo1_slider.get(), servo2_slider.get(), 
                servo3_slider.get(), servo4_slider.get()]
    saved_positions.append(position)
    positions_listbox.insert(END, f"Pos {len(saved_positions)}: {position}")
    print("Saved positions: " + str(saved_positions))

def play_positions():
    if not port_opened:
        messagebox.showwarning("Warning", "Please connect to Arduino first!")
        return
    
    if not saved_positions:
        messagebox.showwarning("Warning", "No positions saved!")
        return
    
    for i, position in enumerate(saved_positions):
        print(f"Playing position {i+1}: {position}")
        send_positions(position)
        time.sleep(1)
    print("Finished playing all positions")

def clear_all_positions():
    global saved_positions
    saved_positions = []
    positions_listbox.delete(0, END)
    print("Cleared all positions")

def clear_last_position():
    global saved_positions
    if saved_positions:
        removed = saved_positions.pop()
        positions_listbox.delete(END)
        print("Removed: " + str(removed))
    else:
        print("No positions to remove")

def open_file():
    global saved_positions
    filename = filedialog.askopenfilename(
        initialdir="/", 
        title="Select a File", 
        filetypes=(("Text files", "*.txt*"), ("all files", "*.*"))
    )
    if filename:
        try:
            file = open(filename, "r")
            data = file.read()
            saved_positions = eval(data)
            file.close()
            
            # Update listbox
            positions_listbox.delete(0, END)
            for i, pos in enumerate(saved_positions):
                positions_listbox.insert(END, f"Pos {i+1}: {pos}")
            
            print("Opened: " + filename)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file\n{str(e)}")

def save_file():
    if not saved_positions:
        messagebox.showwarning("Warning", "No positions to save!")
        return
    
    save_file = filedialog.asksaveasfile(
        mode='w', 
        defaultextension=".txt",
        filetypes=(("Text files", "*.txt"), ("all files", "*.*"))
    )
    if save_file:
        save_file.write(str(saved_positions))
        save_file.close()
        print("Saved file")

def instructions():
    msg = """ROBOT ARM CONTROLLER - INSTRUCTIONS

1. Set Arduino COM Port:
   - Find COM port in Device Manager (Windows)
   - Enter port name (e.g., COM3) and click Connect
   
2. Control Servos:
   - Use sliders to move servos in real-time
   - Servo 1 (MG995): Base rotation
   - Servo 2 (MG996R): Shoulder
   - Servo 3 (SG90): Elbow
   - Servo 4 (SG90): Gripper
   
3. Record Positions:
   - Move servos to desired position
   - Click "Record Position" to save
   
4. Replay Positions:
   - Click "Replay Positions" to play sequence
   
5. Save/Load:
   - File > Save File: Save positions to file
   - File > Open File: Load saved positions
"""
    messagebox.showinfo("Instructions", msg)
    print(msg)

def update_servo_positions():
    """Function to continuously send servo positions"""
    while running:
        if port_opened:
            try:
                send_positions([servo1_slider.get(), servo2_slider.get(), 
                               servo3_slider.get(), servo4_slider.get()])
            except:
                pass
        time.sleep(0.05)

def on_closing():
    """Handle window closing"""
    global running, arduino, port_opened
    running = False
    if port_opened and arduino:
        arduino.close()
    window.destroy()

# Create main window
window = Tk()
window.title("Robot Arm Controller - 4 Servo")
window.geometry("520x580")
window.resizable(False, False)
window.protocol("WM_DELETE_WINDOW", on_closing)

# Port settings frame
port_frame = LabelFrame(window, text="Arduino Connection", padx=10, pady=5)
port_frame.place(x=10, y=10, width=500, height=90)

port_label = Label(port_frame, text="COM Port:")
port_label.grid(row=0, column=0, sticky=W, padx=5)

port_input = Entry(port_frame, width=15)
port_input.grid(row=0, column=1, padx=5)
port_input.insert(0, "COM3")

port_button = Button(port_frame, text="Connect", command=set_port, bg="lightblue", width=10)
port_button.grid(row=0, column=2, padx=5)

status_label = Label(port_frame, text="Status: Not Connected", fg="red", font=("Arial", 9, "bold"))
status_label.grid(row=1, column=0, columnspan=3, pady=5)

# Servo control frame
servo_frame = LabelFrame(window, text="Servo Control", padx=5, pady=5)
servo_frame.place(x=10, y=110, width=500, height=180)

# Servo 1 - MG995
servo1_label = Label(servo_frame, text="Servo 1 (MG995)\nBase", font=("Arial", 8))
servo1_label.grid(row=0, column=0, padx=8)
servo1_slider = Scale(servo_frame, from_=180, to=0, length=130)
servo1_slider.grid(row=1, column=0, padx=8)
servo1_slider.set(90)

# Servo 2 - MG996R
servo2_label = Label(servo_frame, text="Servo 2 (MG996R)\nShoulder", font=("Arial", 8))
servo2_label.grid(row=0, column=1, padx=8)
servo2_slider = Scale(servo_frame, from_=180, to=0, length=130)
servo2_slider.grid(row=1, column=1, padx=8)
servo2_slider.set(90)

# Servo 3 - SG90
servo3_label = Label(servo_frame, text="Servo 3 (SG90)\nElbow", font=("Arial", 8))
servo3_label.grid(row=0, column=2, padx=8)
servo3_slider = Scale(servo_frame, from_=180, to=0, length=130)
servo3_slider.grid(row=1, column=2, padx=8)
servo3_slider.set(90)

# Servo 4 - SG90
servo4_label = Label(servo_frame, text="Servo 4 (SG90)\nGripper", font=("Arial", 8))
servo4_label.grid(row=0, column=3, padx=8)
servo4_slider = Scale(servo_frame, from_=180, to=0, length=130)
servo4_slider.grid(row=1, column=3, padx=8)
servo4_slider.set(90)

# Position control frame
control_frame = LabelFrame(window, text="Position Control", padx=10, pady=10)
control_frame.place(x=10, y=300, width=500, height=100)

save_button = Button(control_frame, text="Record Position", command=save_positions, 
                     bg="lightgreen", width=18, height=1)
save_button.grid(row=0, column=0, padx=5, pady=5)

play_button = Button(control_frame, text="Replay Positions", command=play_positions, 
                     bg="lightblue", width=18, height=1)
play_button.grid(row=0, column=1, padx=5, pady=5)

clear_last_button = Button(control_frame, text="Clear Last", command=clear_last_position, 
                           bg="yellow", width=18, height=1)
clear_last_button.grid(row=1, column=0, padx=5, pady=5)

clear_all_button = Button(control_frame, text="Clear All", command=clear_all_positions, 
                          bg="orange", width=18, height=1)
clear_all_button.grid(row=1, column=1, padx=5, pady=5)

# Saved positions listbox
positions_frame = LabelFrame(window, text="Saved Positions", padx=10, pady=5)
positions_frame.place(x=10, y=410, width=500, height=130)

scrollbar = Scrollbar(positions_frame)
scrollbar.pack(side=RIGHT, fill=Y)

positions_listbox = Listbox(positions_frame, height=6, width=70, yscrollcommand=scrollbar.set)
positions_listbox.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=positions_listbox.yview)

# Menu bar
menubar = Menu(window)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open File", command=open_file)
filemenu.add_command(label="Save File", command=save_file)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=on_closing)
menubar.add_cascade(label="File", menu=filemenu)

editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Clear Last Position", command=clear_last_position)
editmenu.add_command(label="Clear All Positions", command=clear_all_positions)
menubar.add_cascade(label="Edit", menu=editmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Instructions", command=instructions)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)

# Start background thread for servo updates
servo_thread = threading.Thread(target=update_servo_positions, daemon=True)
servo_thread.start()

# Run the GUI
window.mainloop()