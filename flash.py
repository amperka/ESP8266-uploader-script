#!/usr/bin/env python3
"""
    Script for easy update esp8266 firmware with esptool.
    * Run script with command: ./flash.py
    * The script works with python version higher than 3.7.
    * You must have esptool on your PC.
    * You can check it with command in terminal: esptool version
    * First, choose serial port device, then choose firmware.
    * You can choose your firmware. Add it to directory ./firmwares.
    * Script has pre-downloaded firmware AT commands and espruino v2.06 for esp8266 2MB and 4MB
"""


import os
import subprocess
import re
import sys


def get_esptool_command():
    """check platform and form esptool command"""
    if sys.platform == "linux" or sys.platform == "linux2":
        esptool = "esptool"
    elif sys.platform == "darwin":
        esptool = "esptool.py"
    return esptool


ESPTOOL = get_esptool_command()


def exit_with_enter(error):
    """function for exit with enter"""
    print("Press Enter to exit.")
    input()
    sys.exit(error)


def check_esptool():
    """function for check esptool on device"""
    try:
        output = subprocess.run(
            [ESPTOOL, "version"],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        if re.search(".*esptool.*", output.stdout) is not None:
            return True
        return False
    except FileNotFoundError:
        return False


def get_number(max_input):
    """get correct number from 0 to max_input"""
    num = 0
    while True:
        try:
            num = int(input())
            if max_input > num >= 0:
                break
            raise ValueError
        except(TypeError, ValueError):
            print("Print a correct number.")
    return num


def do_esptool_command(command, to_console=False):
    """do esptool command in console with subprocess"""
    try:
        if to_console:
            return subprocess.run(
                command,
                text=True,
                check=True
            )
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as error:
        print("")
        if error.returncode == 2:
            print("Error: The ./firmwares directory not found.")
            print("The working directory should be a clone of \
                   https://github.com/amperka/ESP8266-uploader-script")
        elif error.returncode == 1 or error.returncode == 5:
            print("Error: connection lost. Reconnect your board and relaunch script.")
        else:
            print(error.stderr)
        exit_with_enter(error.returncode)


def get_serial_port_list():
    """get list with available serial port devices USB and ACM"""
    ports = os.listdir("/dev/")
    output = []
    for item in ports:
        if sys.platform == "darwin" and item.startswith("tty."):
            output.append(item)
        elif (re.search("ttyUSB*", item) is not None) or (
                re.search("ttyACM*", item) is not None):
            output.append(item)
    return output


def get_serial_port():
    """get string with serial port device name from user"""
    print()
    ports = get_serial_port_list()
    while len(ports) == 0:
        print(
            "You have not any serial port devices. Plug in your Espressif device. Then press ENTER."
        )
        input()
        ports = get_serial_port_list()
    print("available serial port devices:")
    for i, item in enumerate(ports, 0):
        print(str(i) + " " + item)
    print("Choose your port. Print number of your serial port device.")
    return ports[get_number(len(ports))]


def get_firmware_list():
    """get directories with firmwares for esptool"""
    return os.listdir("./firmwares/")


def get_firmware():
    """get name of firmware from user"""
    print()
    firmwares = get_firmware_list()
    while len(firmwares) == 0:
        print("Error: The ./firmwares directory not found.")
        print("The working directory should be a clone of \
              https://github.com/amperka/ESP8266-uploader-script")
        exit_with_enter(2)
    print("available firmwares:")
    for i, item in enumerate(firmwares, 0):
        print(str(i) + " " + item)
    print("Choose your firmware. Print number of your firmware.")
    return firmwares[get_number(len(firmwares))]


def get_esp_flash_size(serial_port):
    """get esp8266 flash size for correct firmware"""
    out = do_esptool_command([ESPTOOL, "--port", "/dev/" + serial_port, "flash_id"], False)
    return re.search(".MB", out.stdout).group(0)


def flash(serial_port, firmware_path):
    """flash board with esptool"""
    do_esptool_command([
        ESPTOOL,
        "--port",
        "/dev/" + serial_port,
        "write_flash",
        "0x0000",
        firmware_path], True)



def main():
    """main function"""
    try:
        if not check_esptool():
            print("Esptool is not installed.")
            print("Install esptool on Debian with command: sudo apt install esptool")
            print("If you have mac use: brew install esptool")
            print("You can install esptool with pip: pip install esptool")
            exit_with_enter(76)
        serial_port_name = get_serial_port()
        firmware_name = get_firmware()
        if os.path.isdir("./firmwares/" + firmware_name):
            firmware_path = (
                "./firmwares/" + firmware_name + "/" + get_esp_flash_size(serial_port_name) + ".bin"
            )
        else:
            firmware_path = "./firmwares/" + firmware_name
        flash(serial_port_name, firmware_path)
        print("Firmware update was successful.")
        exit_with_enter(0)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(130)

if __name__ == "__main__":
    main()
