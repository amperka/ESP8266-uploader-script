echo 'available COM ports:'
echo ''

$tempCOMPortList = (Get-WmiObject -query "SELECT * FROM Win32_PnPEntity" | Where {$_.Name -Match "COM\d+"})
$COMPortList = @()
$i = 0
ForEach ($fullCOMPort in $tempCOMPortList){
    $temp = $fullCOMPort.name
    $number = $(($temp -split " " -match "COM")[0].TrimStart("(").TrimEnd(")"))
    $COMPortList+=$number
    echo "$($i): $($number) $($fullCOMPort.description)"
    $i += 1
}

echo ''
echo ''
echo 'Choose your port. Print number of your COM port.'
[int]$comPortIndex = read-host

echo ''
echo ''



..\esptool.exe `
						--port $($COMportList[$comPortIndex]) `
						write_flash 0x1FC000 esp_init_data_default.bin `
                                    0xFE000 blank.bin `
                                    0x1FE000 blank.bin `
                                    0x00000 boot_v1.6.bin `
                                    0x01000 espruino_esp8266_user1.bin `
                        --erase-all

#..\esptool.exe read_flash 0x00000000 2097152  espruino_2MB.bin