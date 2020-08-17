#!/usr/bin/env python3
import os
import subprocess
import re

def downloadESPtool():
    output = subprocess.run(["sudo", "apt", "install", "esptool"], text=True)
    if(output.returncode != 0):
        raise Exeption(output.returncode)
        
def getNumber(maxInput):
    num = 0
    while True:
        try:
            num = int(input())
            if (num >= 0 and num < maxInput):
                break;
            else: 
                raise Exception("Wrong input number")
        except:
            print("Print a correct number.")
    return num
    
def getCOMPortList():
    ports = os.listdir("/dev/")
    output = []
    for i in range(len(ports) - 1):
        if((re.search("ttyUSB*", ports[i]) != None) or (re.search("ttyACM*", ports[i]) != None)):
            output.append(ports[i]);
    return output
    
def getCOMPort():
    print()
    ports = getCOMPortList()
    while (len(ports) == 0):
        print("You have not any COM ports. Plug in your Espressif device. Then press ENTER.")
        input()
        ports = getCOMPorts()
    print("available COM ports:")
    for i in range(len(ports)):
        print(str(i) + " " + ports[i])
    print("Choose your port. Print number of your COM port.")
    return ports[getNumber(len(ports))]

def getFirmwareList():
    return os.listdir("./firmwares/")
    
def getFirmware():
    print()
    firmwares = getFirmwareList()
    while (len(firmwares) == 0):
        print("Error: firmares are lost. Reload this folder from http://wiki.amperka.ru/")
        input()
        exit()
    print("available firmwares:")
    for i in range(len(firmwares)):
        print(str(i) + " " + firmwares[i])
    print("Choose your firmware. Print number of your firmware.")
    return firmwares[getNumber(len(firmwares))]

def getESPFlashSize(COMPort):
    out = subprocess.run(["esptool", "--port", "/dev/" + COMPort, "flash_id"], stdout=subprocess.PIPE, text=True)
    if(out.returncode != 0):
        raise Exception(out.returncode)
    return re.search(".MB", out.stdout).group(0)

def flash(COMPort, firmwarePath):
    out = subprocess.run(["esptool", 
                          "--port", "/dev/" + COMPort,
                          "write_flash", "0x0000", firmwarePath], text=True)
    if(out.returncode != 0):
        raise Exception(out.returncode)



try:
    downloadESPtool()
    COMPort = getCOMPort()
    firmware = "./firmwares/" + getFirmware() + "/" + getESPFlashSize(COMPort) + ".bin"
    flash(COMPort, firmware)
except Exception as e:
    print(e);
    if(str(e) == "2"):
        print("Error: firmares are lost. Reload this folder from http://wiki.amperka.ru/")
    elif(str(e) == "1"):
        print("Error: connection lost. Reconnect your board and relaunch script.")
else:
    print("Firmware update was successful.")
finally:
    print("Press Enter to exit.")
    input()
