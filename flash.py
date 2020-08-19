#!/usr/bin/env python3
"""
    Script for easy update esp8266 firmware with esptool.
    * Run script with command: ./flash.py
    * The script works with python version higher than 3.7.
    * You must have esptool on your PC.
    * You can check it with command in terminal: esptool version
    * First, choose COM port, then choose firmware.
    * You can choose your firmware. Add it to folder firmwares.
    * Script has pre-downloaded firmware AT commands and espruino v2.06 for esp8266 2MB and 4MB
"""

import os
import subprocess
import re
import sys

def exit_with_enter(error):
    """function for exit with enter"""
    print("Press Enter to exit.")
    input()
    sys.exit(error)


def check_esptool():
    """function for check esptool on device"""
    try:
        output = subprocess.run(
            ["esptool", "version"],
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
            print("Error: firmares are lost. Reload this folder from your source.")
        elif error.returncode == 1 or error.returncode == 5:
            print("Error: connection lost. Reconnect your board and relaunch script.")
        else:
            print(error.stderr)
        exit_with_enter(error.returncode)


def get_com_port_list():
    """get list with available com ports USB and ACM"""
    ports = os.listdir("/dev/")
    output = []
    for item in ports:
        if (re.search("ttyUSB*", item) is not None) or (
                re.search("ttyACM*", item) is not None):
            output.append(item)
    return output


def get_com_port():
    """get string with com port name from user"""
    print()
    ports = get_com_port_list()
    while len(ports) == 0:
        print(
            "You have not any COM ports. Plug in your Espressif device. Then press ENTER."
        )
        input()
        ports = get_com_port_list()
    print("available COM ports:")
    for i, item in enumerate(ports, 0):
        print(str(i) + " " + item)
    print("Choose your port. Print number of your COM port.")
    return ports[get_number(len(ports))]


def get_firmware_list():
    """get directories with firmwares for esptool"""
    return os.listdir("./firmwares/")


def get_firmware():
    """get name of firmware from user"""
    print()
    firmwares = get_firmware_list()
    while len(firmwares) == 0:
        print(
            "Error: firmares are lost. Reload this folder from http://wiki.amperka.ru/"
        )
        exit_with_enter(2)
    print("available firmwares:")
    for i, item in enumerate(firmwares, 0):
        print(str(i) + " " + item)
    print("Choose your firmware. Print number of your firmware.")
    return firmwares[get_number(len(firmwares))]


def get_esp_flash_size(com_port):
    """get esp8266 flash size for correct firmware"""
    out = do_esptool_command(["esptool", "--port", "/dev/" + com_port, "flash_id"], False)
    return re.search(".MB", out.stdout).group(0)


def flash(com_port, firmware_path):
    """flash board with esptool"""
    do_esptool_command([
        "esptool",
        "--port",
        "/dev/" + com_port,
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
        com_port_name = get_com_port()
        firmware_name = get_firmware()
        if os.path.isdir("./firmwares/" + firmware_name):
            firmware_path = (
                "./firmwares/" + firmware_name + "/" + get_esp_flash_size(com_port_name) + ".bin"
            )
        else:
            firmware_path = "./firmwares/" + firmware_name
        flash(com_port_name, firmware_path)
        print("Firmware update was successful.")
        exit_with_enter(0)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(130)

if __name__ == "__main__":
    main()
