:loop

taskkill /IM VPN.exe


echo "STARTING..."
cmd.exe /c "start ./VPN.exe"



timeout 60

echo " Killing the VPN"
taskkill /IM VPN.exe

timeout 10

goto loop