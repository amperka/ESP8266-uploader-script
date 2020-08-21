Function Read-Number(){
    #read int from console
    $Output = Read-Host
    #check input
    while(!($Output -match "^\d{1,5}$")){
        Write-Host "Print a correct number."
        $Output = Read-Host
    }
    Return($Output)
}

Function Write-COMPorts(){
    #write com port list to console
    Write-Host "available COM ports:"
    #get coms array from database and grep it 
    $TempCOMPortList = (Get-WmiObject -query "SELECT * FROM Win32_PnPEntity" | Where-Object {$_.Name -Match "COM\d+"})
    $COMPortList = @()
    $i = 0
    #write array to console
    ForEach ($FullCOMPort in $TempCOMPortList){
        $Temp = $FullCOMPort.name
        $Number = $(($Temp -split " " -match "COM")[0].TrimStart("(").TrimEnd(")"))
        $COMPortList+=$Number
        Write-Host "$($i): $($Number) $($FullCOMPort.description)"
        $i += 1
    }
    Write-Host ""
    return($COMPortList)
}

Function Get-COMPort(){
    #ask user number of com
    $COMPortList = Write-COMPorts
    #check count of com ports
    while($COMPortList.Length -eq 0){
        Write-Host "You have not any COM ports. Plug in your Espressif device. Then press ENTER."
        Read-Host
        $COMPortList = Write-COMPorts
    }
    Write-Host "Choose your port. Print number of your COM port."
    [int]$COMPortIndex = Read-Number
    #check number of com ports
    while(($COMPortIndex -lt 0) -or ($COMPortIndex -gt $COMPortList.Length - 1)){
        Write-Host "Print a correct number."
        $COMPortIndex = Read-Number
    }
    Return($COMportList[$COMPortIndex])
}

Function Write-Firmwares(){
    #print array of firmwares to console
    Write-Host "available firmwares:"
    #get all items in .\firmwares
    $FirmwareList = Get-ChildItem -Path ".\firmwares\"
    $i = 0
    #print items
    ForEach ($Firmvare in $FirmwareList) {  
        Write-Host "$($i): $($Firmvare.Name)"
        $i = $i + 1 
    } 
    Write-Host ""
    return($FirmwareList)
}

Function Get-Firmwares(){
    #get firmware from user
    $FirmwareList = Write-Firmwares
    #check count of firmwares
    if($FirmwareList.Length -eq 0){
        Write-Host "Error: The ./firmwares directory not found."
        Write-Host "The working directory should be a clone of `
                    https://github.com/amperka/ESP8266-uploader-script"
        Read-Host
        Exit
    }
    Write-Host "Choose your firmware. Print number of your firmware."
    [int]$FirmwareIndex = Read-Number
    #check number of firmware
    while(($FirmwareIndex -lt 0) -or ($FirmwareIndex -gt $FirmwareList.Length - 1)){
        Write-Host "Print a correct number."
        $FirmwareIndex = Read-Number
    }
    return($FirmwareList[$FirmwareIndex]) 
}

Function Read-Directory($Dir){
    #is this Dir folder or file
    #return True or False
    return((Get-Item $Dir.FullName) -is [System.IO.DirectoryInfo])
}

Function Write-Error(){
    #check return code of esptool and print errors 
    if($LastExitCode -eq 0){
        Write-Output "Firmware update was successful."
    } elseif(($LastExitCode -eq -1) -or ($LastExitCode -eq -5)){
        Write-Output "Error: connection lost. Reconnect your board and relaunch script."
    } elseif($LastExitCode -eq 2){
        Write-Output "Error: failed to connect to Espressif device: Timed out waiting for packet header. Check the wires and do not forget to push the PROG button."
    } 
    Write-Host "Press Enter to exit."
    Read-Host
}

Function Get-ESPFlashSize($COMPort){
    #check esp flash size
    #return string f.e. 2MB
    Return $(.\esptool\esptool.exe --port $COMPort flash_id) -match ".MB" -split " " -match ".MB"
}

Function Flash($COMPort, $FirmwarePath){
    #flash firmware whith esptool
    .\esptool\esptool.exe `
						   --port $COMPort `
						   write_flash 0x0000  $FirmwarePath `
						   --erase-all
}

$COMPort = Get-COMPort
$FirmwarePath = Get-Firmwares
if(!(Read-Directory $FirmwarePath)){
    Flash $COMPort $FirmwarePath.FullName
}else{       
    Flash $COMPort "$($FirmwarePath.FullName)\$(Get-ESPFlashSize($COMPort)).bin"
}

Write-Error
