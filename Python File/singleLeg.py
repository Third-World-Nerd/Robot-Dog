# import tkinter as tk
# from tkinter import ttk
# import serial
# import time

# # === Serial Setup ===
# try:
#     ser = serial.Serial('COM8', 9600, timeout=1)  # CHANGE THIS PORT
#     time.sleep(2)
#     print("Serial connected.")
# except serial.SerialException:
#     ser = None
#     print("Failed to connect to serial port.")

# # === Constants ===
# NUM_LEGS = 4
# NUM_JOINTS = 3
# LEG_LABELS = ['Leg 1', 'Leg 2', 'Leg 3', 'Leg 4']
# JOINT_LABELS = ['Hip', 'Femur', 'Fibula']
# DEFAULT_ANGLES = [68, -33, 0, 68, -33, 0, 84, -33, 0, 84, -33, 0]   # [105, -60, 0, 105, -60, 0, ...]

# # === GUI Setup ===
# root = tk.Tk()
# root.title("Quadruped Servo Controller")
# root.geometry("600x600")

# sliders = []

# def send_angles():
#     angles = [slider.get() for slider in sliders]
#     if ser and ser.is_open:
#         try:
#             data_string = ','.join(str(int(a)) for a in angles)
#             framed_message = f"<{data_string}>\n"
#             ser.write(framed_message.encode())
#             print("Sent:", framed_message.strip())
#         except Exception as e:
#             print("Error:", e)

# # === Slider Grid ===
# slider_frame = tk.Frame(root)
# slider_frame.pack(pady=20)

# for leg in range(NUM_LEGS):
#     leg_label = tk.Label(slider_frame, text=LEG_LABELS[leg], font=('Arial', 12, 'bold'))
#     leg_label.grid(row=leg * (NUM_JOINTS + 1), column=0, columnspan=2, pady=(10, 0))

#     for joint in range(NUM_JOINTS):
#         idx = leg * NUM_JOINTS + joint
#         label = tk.Label(slider_frame, text=JOINT_LABELS[joint])
#         label.grid(row=leg * (NUM_JOINTS + 1) + joint + 1, column=0)

#         slider = tk.Scale(slider_frame, from_=-180, to=180, orient='horizontal', length=400,
#                           command=lambda val: send_angles())  # Update on move
#         slider.set(DEFAULT_ANGLES[idx])
#         slider.grid(row=leg * (NUM_JOINTS + 1) + joint + 1, column=1)
#         sliders.append(slider)

# # === Buttons ===
# button_frame = tk.Frame(root)
# button_frame.pack(pady=20)

# def reset_to_default():
#     for i, slider in enumerate(sliders):
#         slider.set(DEFAULT_ANGLES[i])
#     send_angles()

# reset_button = tk.Button(button_frame, text="Reset to Default", command=reset_to_default, width=20)
# reset_button.pack()

# root.mainloop()



import tkinter as tk
from tkinter import ttk
import serial
import time
import datetime

# === Serial Setup ===
try:
    ser = serial.Serial('COM8', 9600, timeout=1)  # CHANGE THIS PORT AS NEEDED
    time.sleep(2)
    print("Serial connected.")
except serial.SerialException:
    ser = None
    print("Failed to connect to serial port.")

# === Constants ===
NUM_LEGS = 4
NUM_JOINTS = 3
LEG_LABELS = ['Leg 1', 'Leg 2', 'Leg 3', 'Leg 4']
JOINT_LABELS = ['Hip', 'Femur', 'Fibula']
DEFAULT_ANGLES = [68, -33, 0, 68, -33, 0, 84, -33, 0, 84, -33, 0]   # [105, -60, 0, ...]

# === GUI Setup ===
root = tk.Tk()
root.title("Quadruped Servo Controller")
root.geometry("600x600")

sliders = []
log_data = []  # To store (timestamp, angle list)

def send_angles():
    angles = [slider.get() for slider in sliders]
    if ser and ser.is_open:
        try:
            data_string = ','.join(str(int(a)) for a in angles)
            framed_message = f"<{data_string}>\n"
            ser.write(framed_message.encode())

            # === Timestamp Logging ===
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            log_entry = (timestamp, angles.copy())
            log_data.append(log_entry)

            print(f"{timestamp} -> Sent: {framed_message.strip()}")
        except Exception as e:
            print("Error:", e)

# === Slider Grid ===
slider_frame = tk.Frame(root)
slider_frame.pack(pady=20)

for leg in range(NUM_LEGS):
    leg_label = tk.Label(slider_frame, text=LEG_LABELS[leg], font=('Arial', 12, 'bold'))
    leg_label.grid(row=leg * (NUM_JOINTS + 1), column=0, columnspan=2, pady=(10, 0))

    for joint in range(NUM_JOINTS):
        idx = leg * NUM_JOINTS + joint
        label = tk.Label(slider_frame, text=JOINT_LABELS[joint])
        label.grid(row=leg * (NUM_JOINTS + 1) + joint + 1, column=0)

        slider = tk.Scale(slider_frame, from_=-180, to=180, orient='horizontal', length=400,
                          command=lambda val: send_angles())  # Update on move
        slider.set(DEFAULT_ANGLES[idx])
        slider.grid(row=leg * (NUM_JOINTS + 1) + joint + 1, column=1)
        sliders.append(slider)

# === Buttons ===
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

def reset_to_default():
    for i, slider in enumerate(sliders):
        slider.set(DEFAULT_ANGLES[i])
    send_angles()

reset_button = tk.Button(button_frame, text="Reset to Default", command=reset_to_default, width=20)
reset_button.pack()

# === Handle Exit & Save Log ===
def on_closing():
    if ser and ser.is_open:
        ser.close()
    # Save log to file
    with open("servo_log.csv", "w") as f:
        f.write("Timestamp," + ",".join(f"J{i+1}" for i in range(NUM_LEGS * NUM_JOINTS)) + "\n")
        for timestamp, angles in log_data:
            f.write(f"{timestamp}," + ",".join(str(a) for a in angles) + "\n")
    print("Log saved to servo_log.csv")
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# === Start GUI ===
root.mainloop()
