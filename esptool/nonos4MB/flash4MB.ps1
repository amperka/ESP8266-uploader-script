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
						write_flash  0x00000 eagle.flash.bin `
                                     0x10000 eagle.irom0text.bin `
                                     0x3FE000 blank.bin `
                                     0x7E000 blank.bin `
                                     0x3FC000 esp_init_data_default_v08.bin `
                        --erase-all
#..\esptool.exe read_flash 0x00000000 4194304  espruino_4MB.bin