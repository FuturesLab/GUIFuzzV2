import pyautogui
import time
import random
import sys
import os
from multiprocessing import Process
import math
import subprocess
import chardet
import re

seed_path = './out/.cur_input'
start_window = ""

if len(sys.argv) > 2 and sys.argv[1] != None and sys.argv[2] != None:
    target_program = sys.argv[1]
    seed_path = sys.argv[2]

    def task():
        os.system(target_program)


    process = Process(target=task)
    process.start()


def getWindowCoords():
    global start_window
    window_list = []  # start x, start y, width, height
    try:
        window_command = "xwininfo -id $(xdotool getactivewindow)"
        window_info = subprocess.check_output(window_command, shell=True, stderr=subprocess.STDOUT)

        window_info = window_info.decode('utf-8')
        info = window_info.split("\n")
        if start_window == "":
            start_window = re.search(r'Window id: (\S+)', info[1]).group(1)

    except subprocess.CalledProcessError as e:
        # Handle errors from subprocess, such as command failure
        print(f"Error occurred while executing command: {e}")
        print(f"Output was: {e.output.decode('utf-8')}")
        return [0, 0, 0, 0]

    for res in info:
        temp = res.split(":")
        if (len(temp) > 1):
            match temp[0].strip():
                case "Absolute upper-left X":
                    window_list.append(int(temp[1].strip()))
                case "Absolute upper-left Y":
                    window_list.append(int(temp[1].strip()))
                case "Width":
                    window_list.append(int(temp[1].strip()))
                case "Height":
                    window_list.append(int(temp[1].strip()))
    return window_list


def getScreenResolution():
    resolution_command = "xdpyinfo | grep dimensions | awk '{ print $2 }'"
    resol_value = subprocess.check_output(resolution_command, shell=True)
    resol_value = resol_value.decode('utf-8')
    resol_value_split = resol_value.split('x')
    return int(resol_value_split[0])


def update_window_coords():
    window_coords = getWindowCoords()
    return window_coords[0], window_coords[1], window_coords[2], window_coords[3]


def execute_click(i, data):
    val = ord(data[i + 1]) / 255.0
    val2 = ord(data[i + 2]) / 255.0

    x_val = start_x + width * val
    if x_val <= start_x:
        x_val = start_x + 1

    y_val = (start_y + y_padding) + (height - y_padding) * val2
    if y_val <= start_y + y_padding:
        y_val = start_y + y_padding + 1

    if width != 0:
        pyautogui.click(math.floor(x_val), math.floor(y_val))


def execute_key(i, data):
    ascii_char = chr(ord(data[i + 1]))
    pyautogui.write(ascii_char)


def execute_lower():
    try:
        window_command = "xwininfo -id $(xdotool getactivewindow)"
        window_info = subprocess.check_output(window_command, shell=True, stderr=subprocess.STDOUT)

        window_info = window_info.decode('utf-8')
        info = window_info.split("\n")

        if re.search(r'Window id: (\S+)', info[1]).group(1) == start_window:
            return

        pyautogui.hotkey('alt', 'f4')

    except subprocess.CalledProcessError as e:
        # Handle errors from subprocess, such as command failure
        print(f"Error occurred while executing command: {e}")
        print(f"Output was: {e.output.decode('utf-8')}")
        return [0, 0, 0, 0]


def choose_operation(byte_value):
    if ord(byte_value) > 245:
        return 'lower'
    elif ord(byte_value) > 241:
        return 'key'
    else:
        return 'click'


time.sleep(30)

y_padding = 10
start_x, start_y, width, height = update_window_coords()

data = ""

with open(seed_path, 'r', encoding='iso-8859-1') as f:
    data = f.read()

i = 0

# Interpret each 2 bytes of data as a click,
# where byte 1 is a percent of the window width and byte 2 is a percent of the window height
while i < len(data):
    if i >= len(data) - 1:
        break

    operation = choose_operation(data[i])

    start_x, start_y, width, height = update_window_coords()

    if operation == 'click':
        execute_click(i, data)
        i += 3
    elif operation == 'key':
        execute_key(i, data)
        i += 2
    elif operation == 'lower':
        execute_lower()
        i += 1

time.sleep(1)

pyautogui.keyDown('ctrlleft')
pyautogui.press('q')
pyautogui.keyUp('ctrlleft')
