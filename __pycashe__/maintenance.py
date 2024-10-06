import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading
from gotify import Gotify
import requests

# Setup Gotify notifications
gotify = Gotify(
    base_url="https://9e3b-109-234-233-4.ngrok-free.app/",
    app_token="A3zhpmK_vQnfhfj"
)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
buzzerpin = 8
GPIO.setup(buzzerpin, GPIO.OUT)
GPIO.output(buzzerpin, GPIO.LOW)

# Maintenance status and timers for each Komax machine
maintenance_status = {i: False for i in range(1, 28)}
timers = {i: 0 for i in range(1, 28)}

# Time and date update
def update_time():
    current_time = time.strftime("Date: %d-%m-%Y Time: %H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_time)

# Toggle maintenance status and start buzzer/timer
def toggle_maintenance(komax_number):
    maintenance_status[komax_number] = not maintenance_status[komax_number]
    button = buttons[komax_number - 1]
    
    if maintenance_status[komax_number]:
        button.config(bg='#007acc', fg='white', relief=tk.SUNKEN)
        threading.Thread(target=activate_buzzer).start()  # Start buzzer in a separate thread
        start_timer(komax_number, button)
        # gotify.create_message(f"Komax {komax_number} called for maintenance", title="SCA", priority=6)
    else:
        reset_maintenance(komax_number)

# Reset maintenance status and button appearance
def reset_maintenance(komax_number):
    maintenance_status[komax_number] = False
    button = buttons[komax_number - 1]
    button.config(bg='#5bc985', fg='black', relief=tk.RAISED, text=f"KOMAX {komax_number}")
    timers[komax_number] = 0

# Activate buzzer
def activate_buzzer():
    GPIO.output(buzzerpin, GPIO.HIGH)
    time.sleep(0.5)  # Short buzzer alert
    GPIO.output(buzzerpin, GPIO.LOW)

# Start the timer for maintenance
def start_timer(komax_number, button):
    if timers[komax_number] == 0:
        timers[komax_number] = 300  # 5 minutes in seconds
        update_timer(komax_number, button)

# Update timer and button color based on remaining time
def update_timer(komax_number, button):
    if maintenance_status[komax_number] and timers[komax_number] > 0:
        minutes, seconds = divmod(timers[komax_number], 60)
        button.config(text=f"KOMAX {komax_number}\nTime: {minutes} min {seconds} sec")

        # Change button color based on remaining time
        if timers[komax_number] == 180:
            button.config(bg='#f9d71c', fg='black')  # Yellow at 3 minutes
        elif timers[komax_number] == 60:
            button.config(bg='red', fg='white')  # Red at 1 minute
        elif timers[komax_number] <= 15:
            button.config(bg='red' if timers[komax_number] % 2 == 0 else '#5bc985')  # Flashing at last 15 seconds

        timers[komax_number] -= 1
        root.after(1000, update_timer, komax_number, button)
    else:
        reset_maintenance(komax_number)

# Tkinter UI setup
root = tk.Tk()
root.title("Komax Maintenance Status")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

buttons = []
for i in range(1, 28):
    button = tk.Button(
        root, text=f"KOMAX {i}", bg='#5bc985', fg='black', font=("Roboto", 16),
        command=lambda i=i: toggle_maintenance(i), padx=10, pady=10, width=10, height=2, relief="groove", borderwidth=5
    )
    buttons.append(button)
    button.grid(row=(i-1) // 5, column=(i-1) % 5, padx=10, pady=10, sticky="nsew")

# Set even distribution of rows/columns
for i in range(5):
    root.grid_columnconfigure(i, weight=1, uniform="col_uniform")
for i in range(6):
    root.grid_rowconfigure(i, weight=1)

time_label = tk.Label(root, text="Time", font=("Roboto", 10), anchor="e")
time_label.grid(row=6, column=4, sticky="ne")

update_time()

# GPIO Setup for Komax machines
row_pins = [17, 18, 22, 23, 24, 25, 5, 6, 12, 13, 19, 14, 20, 2, 16]
col_pins = [26, 21]

# Set up GPIO inputs/outputs
for pin in row_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for pin in col_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

# Operator messages mapped to machines
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
    27: [(21, 2)]
}

# Check button press logic
def check_buttons():
    for col_pin in col_pins:
        GPIO.output(col_pin, GPIO.LOW)
        for row_pin in row_pins:
            if GPIO.input(row_pin) == GPIO.LOW:
                for operator, pins in operator_messages.items():
                    if (col_pin, row_pin) in pins:
                        toggle_maintenance(operator)
        GPIO.output(col_pin, GPIO.HIGH)

# Continuously update maintenance status
def update_maintenance_status():
    check_buttons()
    root.after(400, update_maintenance_status)

update_maintenance_status()
root.mainloop()

# Clean up GPIO on exit
GPIO.cleanup()
