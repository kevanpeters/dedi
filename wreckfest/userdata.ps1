
# Set the installation directory
$installDir = "C:\wreckfest-server"

# Download SteamCMD
Invoke-WebRequest "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -OutFile "steamcmd.zip"
Expand-Archive "steamcmd.zip" -DestinationPath $installDir
Remove-Item "steamcmd.zip"

# Install the Wreckfest server
& "$installDir\steamcmd.exe" +login anonymous +force_install_dir $installDir +app_update 361580 validate +quit

# Set up the config file
# this does not wor
Invoke-WebRequest "https://raw.githubusercontent.com/TheLysdexicOne/wreckfest-server/master/config/server_config.cfg" -OutFile "$installDir\server_config.cfg"

# Open firewall ports
New-NetFirewallRule -DisplayName "Wreckfest Server" -Direction Inbound -LocalPort 27015,27016 -Protocol UDP -Action Allow

# Create a batch file to start the server
"@echo off`ncd $installDir`nserver_run.bat" | Out-File "$installDir\start-server.bat" -Encoding ASCII

# Start the server
Start-Process "$installDir\start-server.bat"