import ctypes
from pynput import mouse, keyboard
import threading
import time
from colorama import init, Fore
import os
from pyautogui import position as positionPy

init(convert=True)

# Color constants for terminal text coloring
LIGHTRED = Fore.LIGHTRED_EX
LIGHT_BLUE = Fore.LIGHTBLUE_EX
RESET = Fore.RESET
BLACK = Fore.LIGHTBLACK_EX
YELLOW = Fore.LIGHTYELLOW_EX

# Flags to control the state of the mouse and the program
mouse_movement_active = False
left_button_pressed = False
right_button_pressed = False
program_running = True

def clear_screen():
    """Clears the command line screen based on the operating system."""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS/BSD/etc
        os.system('clear')

def Input():
    """Handles user input for configuring the recoil control settings."""
    global recoil_delay, move_amount, recoil_delay_ms, TimingPexil, dynamic_recoil_factor, Recoil_Enabled, disable_on_lift
    # Variables for validation
    Meow = 0
    Meow2 = 0
    Meow3 = 0

    # Loop until valid input is received for recoil delay
    while Meow3 == 0:
        try:
            recoil_delay_ms = float(input(f"       {YELLOW}Enter the delay before recoil control start in milliseconds (Recommended '0' ms): "))
            recoil_delay = recoil_delay_ms / 1000  # Convert ms to seconds
            Meow3 = 1
        except ValueError:
            print("       Invalid input. Please enter a number.")

    # Loop until valid input is received for timing between pixel movement
    while Meow == 0:
        TimingPexilAsk = input('       Type timing value between each pixel moved like "20 ms": ')
        if TimingPexilAsk == "":
            TimingPexil = 20
            Meow = 1
        elif float(TimingPexilAsk) <= 0:
            print("       Invalid input. Please enter a number.")
        else:
            try:
                TimingPexil = float(TimingPexilAsk)
                Meow = 1
            except ValueError:
                print("       Invalid input. Please enter a number.")

    # Loop until valid input is received for the amount of pixel movement
    while Meow2 == 0:
        try:
            move_amount = int(input(f"       Enter the amount of pixels to move the mouse down to control recoil (Like '1' pixel per {TimingPexil}ms): "))
            Meow2 = 1
        except ValueError:
            print("       Invalid input. Please enter a number.")

    # Input for enabling dynamic recoil factor
    dynamic_recoil_factor_input = input(f"       Enable dynamic recoil factor? (Type 'N' to disable, press ENTER to enable): ").lower()
    dynamic_recoil_factor = dynamic_recoil_factor_input != "n"
    Recoil_Enabled = "No" if not dynamic_recoil_factor else "Yes"

    # Input for disabling recoil adjustment when aiming upwards
    disable_on_lift_ask = input(f"       Disable recoil adjustment when aiming upwards? (Type 'N' to disable, press ENTER to enable): {RESET}").lower()
    disable_on_lift = disable_on_lift_ask != "n"
    disable_on_lift = "No" if not disable_on_lift else "Yes"

# Ctypes structures for sending input to the system
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("mi", MOUSEINPUT)
    ]

# Recoil manager to calculate and apply the recoil effect
class RecoilManager:

    def __init__(self, slowdown_factor, dynamic_recoil_factor, disable_on_lift):
        global last_mouse_y
        self.slowdown_factor = slowdown_factor
        self.speedup_factor = slowdown_factor * 4
        self.last_mouse_y = last_mouse_y
        self.current_speed = move_amount
        self.dynamic_recoil_factor = dynamic_recoil_factor
        self.disable_on_lift = disable_on_lift

    def update_speed(self):
        """Updates the current speed based on the mouse's Y position."""
        _, y = positionPy()
        y = y - self.last_mouse_y
        if self.disable_on_lift and y < 0:
            # Gradually reduce recoil if the mouse is moving upwards
            dynamic_factor = move_amount / TimingPexil if self.dynamic_recoil_factor else 1.0
            self.current_speed = max(0, self.current_speed - abs(y) / (self.slowdown_factor / dynamic_factor))
        elif self.disable_on_lift and y > 0 :
            # Reset recoil to full strength if the mouse is moving downwards
            self.current_speed = min(move_amount, self.current_speed + abs(y) * self.speedup_factor)


    def apply_recoil(self):
        """Applies the calculated recoil to the mouse position."""
        position(0, int(self.current_speed))

# Function to simulate mouse movement
def move_down():

    """Performs the mouse down movement to simulate recoil."""
    global mouse_movement_active, left_button_pressed, right_button_pressed, dynamic_recoil_factor, disable_on_lift,last_mouse_y
    time.sleep(recoil_delay)
    _,last_mouse_y = positionPy()
    # Set up RecoilManager with dynamic recoil factor
    recoil_manager = RecoilManager(slowdown_factor=1, dynamic_recoil_factor=dynamic_recoil_factor, disable_on_lift=disable_on_lift)  # Slowdown factor will be set inside `update_speed` method

    while left_button_pressed and right_button_pressed and program_running:
        # Update mouse speed using dynamic recoil factor and timing pixel
        recoil_manager.update_speed()
        recoil_manager.apply_recoil()
        time.sleep(TimingPexil / 1000)

def position(dx, dy):
    """Simulates mouse move input to the system."""
    mi = MOUSEINPUT(dx, dy, 0, 0x0001, 0, ctypes.pointer(ctypes.c_ulong(0)))
    inp = INPUT(0, mi)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

# Event handlers for mouse and keyboard
def on_click(x, y, button, pressed):
    """Handles mouse click events."""
    global left_button_pressed, right_button_pressed, mouse_movement_active
    if button == mouse.Button.left:
        left_button_pressed = pressed
    elif button == mouse.Button.right:
        right_button_pressed = pressed

    # Start recoil when both mouse buttons are pressed
    if left_button_pressed and right_button_pressed and not mouse_movement_active and program_running:
        mouse_movement_active = True
        threading.Thread(target=move_down, daemon=True).start()
    # Stop recoil when one of the mouse buttons is released
    elif not left_button_pressed or not right_button_pressed:
        mouse_movement_active = False

def on_press(key):
    """Handles keyboard press events."""
    global program_running, mouse_movement_active
    if key == keyboard.Key.f2:
        # Toggle the running state of the program
        program_running = not program_running
        mouse_movement_active = False
        print(f"       {LIGHTRED} Script paused." if not program_running else f" Script resumed.{RESET}")

def display_logo():
    """Displays the ASCII art logo for the script."""
    ascii_art = """                                                                                        
       RRRRRRRRRRRRRRRRR                                                                           
       R::::::::::::::::R                                                                          
       R::::::RRRRRR:::::R                                                                         
       RR:::::R     R:::::R                                                                        
         R::::R     R:::::R         eeeeeeeeeeee             cccccccccccccccc        ooooooooooo   
         R::::R     R:::::R       ee::::::::::::ee         cc:::::::::::::::c      oo:::::::::::oo 
         R::::RRRRRR:::::R       e::::::eeeee:::::ee      c:::::::::::::::::c     o:::::::::::::::o
         R:::::::::::::RR       e::::::e     e:::::e     c:::::::cccccc:::::c     o:::::ooooo:::::o
         R::::RRRRRR:::::R      e:::::::eeeee::::::e     c::::::c     ccccccc     o::::o     o::::o
         R::::R     R:::::R     e:::::::::::::::::e      c:::::c                  o::::o     o::::o
         R::::R     R:::::R     e::::::eeeeeeeeeee       c:::::c                  o::::o     o::::o
         R::::R     R:::::R     e:::::::e                c::::::c     ccccccc     o::::o     o::::o
       RR:::::R     R:::::R     e::::::::e               c:::::::cccccc:::::c     o:::::ooooo:::::o
       R::::::R     R:::::R      e::::::::eeeeeeee        c:::::::::::::::::c     o:::::::::::::::o
       R::::::R     R:::::R       ee:::::::::::::e         cc:::::::::::::::c      oo:::::::::::oo 
       RRRRRRRR     RRRRRRR         eeeeeeeeeeeeee           cccccccccccccccc        ooooooooooo   
       """
    # Replace characters for colored output
    ascii_art_colored = ascii_art.replace('_',  '_' + RESET)
    for char in "Reco":
        ascii_art_colored = ascii_art_colored.replace(char, LIGHT_BLUE + char + BLACK)

    print(ascii_art_colored+LIGHTRED)
    print(f"       {LIGHT_BLUE}Reco is a Recoil Control Script")
    print("       This Script assists with controlling weapons recoil")
    print("       Developed By Hex")
    print("       IG: _1_B")
    print(f"       {LIGHTRED}This Script is FREE, Source Code on Github @Hexer-7{RESET}")

def display_settings():
    """Displays the current script settings."""
    print(f"       {BLACK}Recoil Control Delay: {LIGHT_BLUE}{recoil_delay_ms}ms{BLACK}")
    print(f"       Recoil Control Timing: {LIGHT_BLUE}{TimingPexil} ms{BLACK}")
    print(f"       Recoil Control Amount: {LIGHT_BLUE}{move_amount} pixels{BLACK}")
    print(f"       Recoil Control Factor: {LIGHT_BLUE}{Recoil_Enabled}{BLACK}")
    print(f"       Recoil Control Disabled when upwards: {LIGHT_BLUE}{disable_on_lift}{BLACK}")
    print(f"       Press {LIGHTRED}F2{BLACK} to pause/resume the script.{RESET}")

def main():
    """Main function to set up and start the script."""
    clear_screen()
    display_logo()
    Input()
    clear_screen()

    display_logo()
    display_settings()

    # Start listening for mouse and keyboard events
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener.start()
    keyboard_listener.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
