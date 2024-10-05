import RPi.GPIO as GPIO
import time
import tkinter as tk
import threading
from gotify import Gotify
import requests
#push notifications

#base_url = "http://192.168.0.23"
#app_token = ".B3X15JI4K-Fmm"

gotify = Gotify(

    base_url = "https://9e3b-109-234-233-4.ngrok-free.app/",
    app_token = "A3zhpmK_vQnfhfj",
        
)

#funksioni baz per message creation
#gotify.create_message("Prova",title="titulli",priority = )




GPIO.setmode(GPIO.BCM)
buzzerpin = 8
GPIO.setup(buzzerpin, GPIO.OUT)
GPIO.output(buzzerpin, GPIO.LOW)

maintenance_status = {i: False for i in range(1, 28)}
timers = {i: 0 for i in range(1, 28)}
#Time and date
def update_time():
    current_time = time.strftime("Date: %d-%m-%Y Time: %H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000,update_time)
    
def toggle_maintenance(komax_number):
    maintenance_status[komax_number] = not maintenance_status[komax_number]
    if maintenance_status[komax_number]:
        button = buttons[komax_number - 1]
        button.config(bg='#007acc', fg='white', relief=tk.SUNKEN)
        #activate buzzer via threading
        buzzer_thread=threading.Thread(target=activate_buzzer)
        buzzer_thread.start()
    
        start_timer(komax_number, button)
        #gotify.create_message(f"Komax {komax_number} called for maintenance",title="SCA",priority = 6)
    else:
        buttons[komax_number - 1].config(bg='#5bc985', fg='black', relief=tk.RAISED)
        
def reset_maintenance(komax_number):
    maintenance_status[komax_number] = False
    buttons[komax_number - 1].config(bg='#5bc985',fg='black',relief = "groove")

def activate_buzzer():
    GPIO.output(buzzerpin, GPIO.HIGH)
    time.sleep(0) #BUZZER TIME KOHA
    GPIO.output(buzzerpin, GPIO.LOW)

def start_timer(komax_number, button):
    if timers[komax_number] == 0:
        timers[komax_number] = 1# 5 minutes in seconds
        update_timer(komax_number, button)

def update_timer(komax_number, button):
    if maintenance_status[komax_number] and timers[komax_number] > 0:
        button.config(text=f"KOMAX {komax_number}\nTime: {timers[komax_number]//60} min {timers[komax_number]%60} sec")
        
        #Different colors on different times
        
        time_left = timers[komax_number]
        #Turn Yellow at minute 3
        if time_left == 180:
            button.config(bg='#f9d71c' ,fg = 'black')
            
        #Turn red at minute 1
        elif time_left == 60:
            button.config(bg='red', fg='white')
            root.after(500, lambda: button.config(bg='f9d71c', fg = 'black'))
        
        elif time_left==15:
            
            if time_left % 2 ==0:
                button.config(bg='FF0000', fg = 'black', relief = tk.RAISED)
                
            else:
                button.config(bg='#5bc985', fg = 'black', relief = tk.RAISED)
        
        
        timers[komax_number] -= 1
        root.after(1000, update_timer, komax_number, button)
        # Color change with different 
    else:
        button.config(text=f"KOMAX {komax_number}")
        timers[komax_number] = 0
        reset_maintenance(komax_number)

root = tk.Tk()
root.title("Komax Maintenance Status")



root.grid_rowconfigure(0, weight=1)  # Make the row expand with the window
root.grid_columnconfigure(0, weight=1)  # Make the column expand with the window

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
        relief="groove",  # Add a border
        borderwidth=5
    )
    
    buttons.append(button)
    row = (i - 1) // 5
    column = (i - 1) % 5
    button.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

# Set column and row weights for even distribution
for i in range(5):
    root.grid_columnconfigure(i, weight=1,uniform = "col_uniform")
for i in range(6):
    root.grid_rowconfigure(i, weight=1)

time_label = tk.Label(root, text = "time",font=("Roboto",10), padx=0, pady=5,anchor = "e")
time_label.grid(row=6, column=4, sticky = "ne")

update_time()





# Define the number of rows and columns in the button matrix for Raspberry Pi
num_rows = 14
num_cols = 2

# Define the GPIO pins for the rows and columns for Raspberry Pi
row_pins = [17, 18, 22, 23, 24, 25, 5, 6, 12, 13, 19, 14, 20,2,16]  # Adjust these to match your setup
#gpio 2 do perdoret vetem per 1 komax gpio 3 eeshte bosh
col_pins = [26, 21]  # Adjust these to match your setup\

GPIO.setmode(GPIO.BCM)

# Set up the row pins with pull-up resistors for Raspberry Pi
for row_pin in row_pins:
    GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up the column pins as outputs for Raspberry Pi
for col_pin in col_pins:
    GPIO.setup(col_pin, GPIO.OUT)
    GPIO.output(col_pin, GPIO.HIGH)  # Initially set the column pins to HIGH

# Operator maintenance messages for Raspberry Pi
operator_messages = {
    1: [(21, 16)],  # KOMAX 1
    2: [(26, 18)],  # KOMAX 2
    3: [(26, 22)],  # KOMAX 3
    4: [(26, 23)],  # KOMAX 4
    5: [(26, 24)],  # KOMAX 5
    6: [(26, 25)],  # KOMAX 6
    7: [(26, 5)],  # KOMAX 7
    8: [(26, 6)],  # KOMAX 8
    9: [(26, 12)],  # KOMAX 9
    10: [(26, 13)],  # KOMAX 10
    11: [(26, 19)],  # KOMAX 11
    12: [(26, 14)],  # KOMAX 12
    13: [(26, 2)],  # KOMAX 13
    14: [(21, 17)],  # KOMAX 14
    15: [(21, 18)],  # KOMAX 15
    16: [(21, 22)],  # KOMAX 16
    17: [(21, 23)],  # KOMAX 17
    18: [(21, 24)],  # KOMAX 18
    19: [(21, 25)],  # KOMAX 19
    20: [(21, 5)],  # KOMAX 20
    21: [(21, 6)],  # KOMAX 21
    22: [(21, 12)],  # KOMAX 22
    23: [(21, 13)],  # KOMAX 23
    24: [(21, 19)],  # KOMAX 24
    25: [(26, 16)],  # KOMAX 25
    26: [(21, 14)],  # KOMAX 26
    27: [(21,2)], #KOMAX 27
    }

    # For example: 3: [(GPIO_COL, GPIO_ROW), (GPIO_COL, GPIO_ROW)],

# Function to check which button is pressed and display maintenance messages for Raspberry Pi
def check_buttons():
    for col_pin in col_pins:
        # Set the column pin low for Raspberry Pi
        GPIO.output(col_pin, GPIO.LOW)

        for row_pin in row_pins:
            if GPIO.input(row_pin) == GPIO.LOW:
                for operator, pins in operator_messages.items():
                    if (col_pin, row_pin) in pins:
                        toggle_maintenance(operator)
        
        # Set the column pin high again for Raspberry Pi
        GPIO.output(col_pin, GPIO.HIGH)

# Function to update maintenance status for Raspberry Pi every 2 seconds
def update_maintenance_status():
    check_buttons()
    root.after(400,update_maintenance_status)

# Start the maintenance status update loop for Raspberry Pi
update_maintenance_status()

# Run the Windows GUI main loop
root.mainloop()

# Cleanup GPIO when the Raspberry Pi application is closed
GPIO.cleanup()
