Function ReadNumber(){
    $Output = Read-Host
    while(!($Output -match "^\d{1,5}$")){
        Write-Host "Print a correct number."
        $Output = Read-Host
    }
    Return($Output)
}

Function PrintCOMPorts(){
    Write-Host "available COM ports:"
    $TempCOMPortList = (Get-WmiObject -query "SELECT * FROM Win32_PnPEntity" | Where {$_.Name -Match "COM\d+"})
    $COMPortList = @()
    $i = 0
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

Function GetCOMPort(){
    $COMPortList = PrintCOMPorts
    while($COMPortList.Length -eq 0){
        Write-Host "You have not any COM ports. Plug in your Espressif device. Then press ENTER."
        Read-Host
        $COMPortList = PrintCOMPorts
    }
    
    Write-Host "Choose your port. Print number of your COM port."
    [int]$COMPortIndex = ReadNumber

    while(($COMPortIndex -lt 0) -or ($COMPortIndex -gt $COMPortList.Length - 1)){
        Write-Host "Print a correct number."
        $COMPortIndex = ReadNumber
    }
    Return($COMportList[$COMPortIndex])
}

Function PrintFirmwares(){
   Write-Host "available firmwares:"
   $FirmwareList = Get-ChildItem -Path ".\firmwares\"
   $i = 0
    ForEach ($Firmvare in $FirmwareList) {  
        Write-Host "$($i): $($Firmvare.Name)"
        $i = $i + 1 
    } 
    Write-Host ""
    return($FirmwareList)
}

Function GetFirmwares(){
    $FirmwareList = PrintFirmwares
    if($FirmwareList.Length -eq 0){
        Write-Host "Error: firmares are lost. Reload this folder from http://wiki.amperka.ru/"
        Read-Host
        Exit
    }
    Write-Host "Choose your firmware. Print number of your firmware."
    [int]$FirmwareIndex = ReadNumber
    while(($FirmwareIndex -lt 0) -or ($FirmwareIndex -gt $FirmwareList.Length - 1)){
        Write-Host "Print a correct number."
        $FirmwareIndex = ReadNumber
    }
    return($FirmwareList[$FirmwareIndex]) 
}

Function IsDirectory($Dir){
    return((Get-Item $Dir.FullName) -is [System.IO.DirectoryInfo])
}

Function PrintError(){
    if($LastExitCode -eq 0){
        echo "Firmware update was successful."
    } elseif($LastExitCode -eq -1){
        echo "Error: connection lost. Reconnect your board and relaunch script."
    } elseif($LastExitCode -eq 2){
        echo "Error: failed to connect to Espressif device: Timed out waiting for packet header. Check the wires and do not forget to push the PROG button."
    }
    Write-Host "Press Enter to exit."
    read-host
}

Function GetESPFlashSize($COMPort){
    $FlashSize = $(.\esptool\esptool.exe --port $COMPort flash_id) -match ".MB" -split " " -match ".MB"
    $Output = [int][string]$FlashSize.Chars(0)
    return($Output)
}

Function Flash($COMPort, $FirmwarePath){
    .\esptool\esptool.exe `
						   --port $COMPort `
						   write_flash 0x0000  $FirmwarePath `
						   --erase-all
}

$COMPort = GetCOMPort
$FirmwarePath = GetFirmwares

if(!(IsDirectory $FirmwarePath)){
    Flash $COMPort $FirmwarePath.FullName
}else{
    $flashSize = GetESPFlashSize($COMPort)
    if($flashSize -eq 2){            
        Flash $COMPort "$($FirmwarePath.FullName)\2MB.bin"
    }elseif($flashSize -eq 4){
        Flash $COMPort "$($FirmwarePath.FullName)\4MB.bin"  
    }else{
        echo "Don't have firmware for your flash size. Do not use this firmware with your board."
        echo "Press Enter to exit."
        Read-Host
        Exit
    }
}

PrintError
