import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading
from gotify import Gotify
from tkinter import messagebox

# Gotify configuration for push notifications
gotify = Gotify(
    base_url="https://9e3b-109-234-233-4.ngrok-free.app/",
    app_token="A3zhpmK_vQnfhfj",
)

# Initialize GPIO settings
GPIO.setmode(GPIO.BCM)
buzzerpin = 8
GPIO.setup(buzzerpin, GPIO.OUT)
GPIO.output(buzzerpin, GPIO.LOW)

# Maintenance status and timers
maintenance_status = {i: False for i in range(1, 28)}
timers = {i: 0 for i in range(1, 28)}

# Function to update time label in the GUI
def update_time():
    current_time = time.strftime("Date: %d-%m-%Y Time: %H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_time)

# Function to toggle maintenance status
def toggle_maintenance(komax_number):
    maintenance_status[komax_number] = not maintenance_status[komax_number]
    button = buttons[komax_number - 1]
    
    if maintenance_status[komax_number]:
        button.config(bg='#007acc', fg='white', relief=tk.SUNKEN)
        threading.Thread(target=activate_buzzer).start()
        start_timer(komax_number, button)

        # Send notification
        gotify.create_message(f"Komax {komax_number} called for maintenance", title="Maintenance Alert", priority=6)
        messagebox.showinfo("Maintenance Alert", f"Komax {komax_number} called for maintenance")
    else:
        button.config(bg='#5bc985', fg='black', relief=tk.RAISED)

# Reset maintenance status
def reset_maintenance(komax_number):
    maintenance_status[komax_number] = False
    buttons[komax_number - 1].config(bg='#5bc985', fg='black', relief="groove")

# Function to activate the buzzer
def activate_buzzer():
    GPIO.output(buzzerpin, GPIO.HIGH)
    time.sleep(1)  # Adjust the duration as needed
    GPIO.output(buzzerpin, GPIO.LOW)

# Function to start the timer
def start_timer(komax_number, button):
    if timers[komax_number] == 0:
        timers[komax_number] = 300  # 5 minutes in seconds
        update_timer(komax_number, button)

# Function to update the timer
def update_timer(komax_number, button):
    if maintenance_status[komax_number] and timers[komax_number] > 0:
        button.config(text=f"KOMAX {komax_number}\nTime: {timers[komax_number] // 60} min {timers[komax_number] % 60} sec")
        time_left = timers[komax_number]

        # Color changes based on remaining time
        if time_left == 180:
            button.config(bg='#f9d71c', fg='black')  # Yellow at 3 minutes
        elif time_left == 60:
            button.config(bg='red', fg='white')  # Red at 1 minute
            root.after(500, lambda: button.config(bg='#f9d71c', fg='black'))  # Flashing effect
        elif time_left == 15:
            button.config(bg='red' if time_left % 2 == 0 else '#5bc985', fg='black', relief=tk.RAISED)  # Flashing red

        timers[komax_number] -= 1
        root.after(1000, update_timer, komax_number, button)
    else:
        button.config(text=f"KOMAX {komax_number}")
        timers[komax_number] = 0
        reset_maintenance(komax_number)

# Create the main GUI window
root = tk.Tk()
root.title("Komax Maintenance Status")

# Configure grid layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

buttons = []
for i in range(1, 28):
    button = tk.Button(
        root,
        text=f"KOMAX {i}",
        bg='#5bc985',  # Green background
        fg='black',
        font=("Roboto", 16),
        command=lambda i=i: toggle_maintenance(i),
        padx=10,
        pady=10,
        width=10,
        height=2,
        relief="groove",
        borderwidth=5
    )
    
    buttons.append(button)
    row = (i - 1) // 5
    column = (i - 1) % 5
    button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

# Set column and row weights for even distribution
for i in range(5):
    root.grid_columnconfigure(i, weight=1, uniform="col_uniform")
for i in range(6):
    root.grid_rowconfigure(i, weight=1)

# Time label
time_label = tk.Label(root, text="time", font=("Roboto", 10), padx=0, pady=5, anchor="e")
time_label.grid(row=6, column=4, sticky="ne")

# Update time
update_time()

# GPIO pin setup for button matrix
row_pins = [17, 18, 22, 23, 24, 25, 5, 6, 12, 13, 19, 14, 20, 2, 16]
col_pins = [26, 21]

for row_pin in row_pins:
    GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for col_pin in col_pins:
    GPIO.setup(col_pin, GPIO.OUT)
    GPIO.output(col_pin, GPIO.HIGH)  # Initially set the column pins to HIGH

# Operator maintenance messages for Raspberry Pi
operator_messages = {
    1: [(21, 16)],
    2: [(26, 18)],
    3: [(26, 22)],
    4: [(26, 23)],
    5: [(26, 24)],
    6: [(26, 25)],
    7: [(26, 5)],
    8: [(26, 6)],
    9: [(26, 12)],
    10: [(26, 13)],
    11: [(26, 19)],
    12: [(26, 14)],
    13: [(26, 2)],
    14: [(21, 17)],
    15: [(21, 18)],
    16: [(21, 22)],
    17: [(21, 23)],
    18: [(21, 24)],
    19: [(21, 25)],
    20: [(21, 5)],
    21: [(21, 6)],
    22: [(21, 12)],
    23: [(21, 13)],
    24: [(21, 19)],
    25: [(26, 16)],
    26: [(21, 14)],
    27: [(21, 2)],
}

# Function to check which button is pressed and display maintenance messages
def check_buttons():
    for col_pin in col_pins:
        GPIO.output(col_pin, GPIO.LOW)
        for row_pin in row_pins:
            if GPIO.input(row_pin) == GPIO.LOW:
                for operator, pins in operator_messages.items():
                    if (col_pin, row_pin) in pins:
                        toggle_maintenance(operator)
        GPIO.output(col_pin, GPIO.HIGH)

# Function to update maintenance status every 2 seconds
def update_maintenance_status():
    check_buttons()
    root.after(2000, update_maintenance_status)

# Start the maintenance status update loop
update_maintenance_status()

# Run the Tkinter main loop
root.mainloop()

# Cleanup GPIO when the application is closed
GPIO.cleanup()
