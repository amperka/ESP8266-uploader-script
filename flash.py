#!/usr/bin/env python3
"""script for easy update esp8266 firmware with esptool"""

import os
import subprocess
import re
import sys

class EsptoolError(Exception):
    """esptool return code exeption"""
    def __init__(self, message):
        super(EsptoolError, self).__init__(message)
        self.message = message


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
    except FileNotFoundError:
        return False
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


def get_com_port_list():
    """get list with available com ports USB and ACM"""
    ports = os.listdir("/dev/")
    output = []
    for i in range(len(ports) - 1):
        if (re.search("ttyUSB*", ports[i]) is not None) or (
                re.search("ttyACM*", ports[i]) is not None):
            output.append(ports[i])
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
        input()
        sys.exit()
    print("available firmwares:")
    for i, item in enumerate(firmwares, 0):
        print(str(i) + " " + item)
    print("Choose your firmware. Print number of your firmware.")
    return firmwares[get_number(len(firmwares))]


def get_esp_flash_size(com_port):
    """get esp8266 flash size for correct firmware"""
    out = subprocess.run(
        ["esptool", "--port", "/dev/" + com_port, "flash_id"],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return re.search(".MB", out.stdout).group(0)


def flash(com_port, firmware_path):
    """flash board with esptool"""
    subprocess.run(
        ["esptool", "--port", "/dev/" + com_port, "write_flash", "0x0000", firmware_path],
        text=True,
        check=True
    )



if not check_esptool():
    print("Esptool is not installed.")
    print("Install esptool on Debian with command: sudo apt install esptool")
    print("If you have mac use: brew install esptool")
    print("You can install esptool with pip: pip install esptool")
    print("Press Enter to exit.")
    input()
    sys.exit()
try:
    com_port_name = get_com_port()
    firmware = (
        "./firmwares/" + get_firmware() + "/" + get_esp_flash_size(com_port_name) + ".bin"
    )
    flash(com_port_name, firmware)
except KeyboardInterrupt:
    print("")
    print("KeyboardInterrupt")
    sys.exit()
except subprocess.CalledProcessError as error:
    print("")
    if error.returncode == 2:
        print("Error: firmares are lost. Reload this folder from your source.")
    elif error.returncode == 1:
        print("Error: connection lost. Reconnect your board and relaunch script.")
    elif error.returncode == 5:
        print("Error: connection lost. Reconnect your board and relaunch script.")
    else:
        print(error.stderr)
else:
    print("Firmware update was successful.")
finally:
    print("Press Enter to exit.")
    input()
