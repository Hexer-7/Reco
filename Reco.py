import subprocess
import sys

required_packages = ['pynput', 'colorama', 'pyautogui']

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check and install required packages
for package in required_packages:
    try:
        __import__(package)
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} not found. Installing {package}...")
        install(package)

import ctypes
from pynput import mouse, keyboard
import threading
import time
from colorama import init, Fore
import os
import pyautogui

init(convert=True)

LIGHTRED = Fore.LIGHTRED_EX  # White text
LIGHT_BLUE = Fore.LIGHTBLUE_EX  # Light blue text
RESET = Fore.RESET  # Reset to default color
BLACK = Fore.LIGHTBLACK_EX
YELLOW = Fore.LIGHTYELLOW_EX
GREEN=Fore.LIGHTBLACK_EX
# Flags to indicate whether the mouse movement is active and the state of mouse buttons
mouse_movement_active = False
left_button_pressed = False
right_button_pressed = False
program_running = True

def clear_screen():
    """Clears the command line screen."""
    # Check OS
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS/BSD/etc
        os.system('clear')

def Input():
    global recoil_delay, move_amount, recoil_delay_ms, TimingPexil, dynamic_recoil_factor,Recoil_Enabled
    Meow = 0
    Meow2 = 0
    Meow3 = 0

    while Meow3 == 0:
        try:
            recoil_delay_ms = float(input(f"    {YELLOW}Enter the delay Before recoil control start in milliseconds (Recommended '0' ms): "))
            recoil_delay = recoil_delay_ms / 1000  # Convert to seconds
            Meow3 = 1
        except:
            print("    Invalid input. Please enter a number.")

    while Meow == 0:
        TimingPexilAsk = input('    Type Timing Value between each Pixels Moved Like "20 ms" (0 Value Increase CPU Usage): ')
        if TimingPexilAsk == "":
            TimingPexil = 20
            Meow = 1
            pass
        else:
            try:
                TimingPexil = float(TimingPexilAsk)
                Meow = 1
            except:
                print("    Invalid input. Please enter a number.")

    while Meow2 == 0:
        try:
            move_amount = int(input(f"    Enter the amount of Pixels to move the mouse down to control recoil (Like '1' Pixels per {TimingPexil}ms): "))
            Meow2 = 1
        except:
            print("    Invalid input. Please enter a number.")

    dynamic_recoil_factor_input = input(f"    Enable dynamic recoil factor? (Type N To Disable, press ENTER To Enable): {RESET}").lower()

    if dynamic_recoil_factor_input == "n":
            dynamic_recoil_factor = False
            Recoil_Enabled = "No"
    else :
        dynamic_recoil_factor = True
        Recoil_Enabled = "Yes"


# Define the necessary structures for SendInput
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class RecoilManager:
    def __init__(self, slowdown_factor, dynamic_recoil_factor):
        self.slowdown_factor = slowdown_factor
        self.speedup_factor = slowdown_factor * 2  # 50% من معامل التباطؤ
        self.last_mouse_y = pyautogui.position()[1]  # Initialize with the current mouse Y position
        self.current_speed = move_amount
        self.dynamic_recoil_factor = dynamic_recoil_factor

    def update_speed(self):
        if self.dynamic_recoil_factor:
            _, y = pyautogui.position()
            movement = y - self.last_mouse_y

            # Calculate dynamic recoil factor based on the number of pixels moved and timing
            dynamic_recoil_factor = abs(movement) / TimingPexil if self.dynamic_recoil_factor else 1.0

            if movement < 0:
                self.current_speed = max(1, self.current_speed - abs(movement) / (self.slowdown_factor / dynamic_recoil_factor))
            else:
                self.current_speed = min(move_amount, self.current_speed + abs(movement) * self.speedup_factor * dynamic_recoil_factor)

            self.last_mouse_y = y

    def apply_recoil(self):
        position(0, int(self.current_speed))



class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("mi", MOUSEINPUT)
    ]

# Function to perform the mouse down movement
def move_down():
    global mouse_movement_active, left_button_pressed, right_button_pressed,dynamic_recoil_factor
    time.sleep(recoil_delay)

    # إعداد RecoilManager مع الميزة الديناميكية لـ Recoil_factor
    recoil_manager = RecoilManager(slowdown_factor=1,dynamic_recoil_factor=dynamic_recoil_factor)  # سيتم تعيين العامل التباطؤ داخل الدالة `update_speed`

    while left_button_pressed and right_button_pressed and program_running:
        # تحديث سرعة الماوس باستخدام الديناميكية لـ Recoil_factor و TimingPexil
        recoil_manager.update_speed()
        recoil_manager.apply_recoil()
        time.sleep(TimingPexil / 1000)
# Function to simulate the mouse move input
def position(dx, dy):
    mi = MOUSEINPUT(dx, dy, 0, 0x0001, 0, ctypes.pointer(ctypes.c_ulong(0)))
    inp = INPUT(0, mi)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

# Mouse click event handler
def on_click(x, y, button, pressed):
    global left_button_pressed, right_button_pressed, mouse_movement_active
    if button == mouse.Button.left:
        left_button_pressed = pressed
    elif button == mouse.Button.right:
        right_button_pressed = pressed

    if left_button_pressed and right_button_pressed and not mouse_movement_active and program_running:
        mouse_movement_active = True
        threading.Thread(target=move_down, daemon=True).start()
    elif not left_button_pressed or not right_button_pressed:
        mouse_movement_active = False

# Keyboard event handler
def on_press(key):
    global program_running,mouse_movement_active
    if key == keyboard.Key.f2:
        # Toggle the running state of the program
        program_running = not program_running
        mouse_movement_active = False
        print(f"{LIGHTRED}    Script paused." if not program_running else f"    Script resumed.{RESET}")
    elif key == keyboard.Key.f3:
        Input()


def display_logo():
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
    print(f"    {LIGHT_BLUE}Reco is Recoil Control Script")
    print("    This Script assists with controlling weapons recoil")
    print("    Developed By Hex")
    print("    IG: _1_B")
    print(f"   {LIGHTRED} This Script is FREE, Source Code on Github @Hexer-7")
    print("\n"+RESET)

def display_settings():
    """Displays the current script settings."""
    print(f"\n    {GREEN}Current Script Settings:")
    print(f"    Recoil Control Delay: {LIGHT_BLUE} {recoil_delay_ms}ms{GREEN}")
    print(f"    Recoil Control Timing: {LIGHT_BLUE}{TimingPexil} ms{GREEN}")
    print(f"    Recoil Control Amount: {LIGHT_BLUE}{move_amount} pixels{GREEN}")
    print(f"    Recoil Control Factor: {LIGHT_BLUE}{Recoil_Enabled}{GREEN}")
    print(f"    Press {LIGHTRED}F2{GREEN} to pause/resume the script.{RESET}")


# Set up and start listening for mouse and keyboard events
def main():
    clear_screen()
    # ASCII Art for the Hexagon logo at the top
    display_logo()
    # Input variables from user
    Input()
    clear_screen()

    # Display logo and settings
    display_logo()
    display_settings()

    # Start listening for mouse and keyboard events
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener.start()
    keyboard_listener.start()

    try:
        while True:
            # The program will keep running until you decide to stop it manually
            time.sleep(1)
    except KeyboardInterrupt:
        # If user interrupts the program (Ctrl+C)
        print("    Exiting Script...")
    finally:
        # Cleanup
        mouse_listener.stop()
        keyboard_listener.stop()
        mouse_listener.join()
        keyboard_listener.join()


if __name__ == "__main__":
    main()
