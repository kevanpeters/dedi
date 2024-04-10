#logs for this user data in C:\Windows\System32\config\systemprofile\AppData\Local\Temp
#disable firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Set the installation directory
$installDir = "C:\wreckfest-server"
$gameDir = "C:\wreckfest-server\steamapps\common\Wreckfest Dedicated Server"

# Download SteamCMD
Invoke-WebRequest "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -OutFile "steamcmd.zip"
Expand-Archive "steamcmd.zip" -DestinationPath $installDir
Remove-Item "steamcmd.zip"

# Install the Wreckfest server
& "$installDir\steamcmd.exe" +login anonymous +force_install_dir $installDir +app_update 361580 validate +quit
# steamcmd.exe +login anonymous +force_install_dir C:\wreckfest-server +app_update 361580 validate +quit


# # Set up the config file
# # this does not wor
Invoke-WebRequest "https://raw.githubusercontent.com/kevanpeters/dedi/main/game_data/wreckfest/config.cfg" -OutFile "$gameDir/server_config.cfg"

#install directx

$url = "https://download.microsoft.com/download/8/4/A/84A35BF1-DAFE-4AE8-82AF-AD2AE20B6B14/directx_Jun2010_redist.exe"
$output = "C:\temp\dxwebsetup.exe"
$extractPath = "C:\temp\dxsetup"
$extractedFile = "$extractPath\DXSETUP.exe"
New-Item -ItemType Directory -Force -Path "C:\temp"
# Download the exe
$wc = New-Object System.Net.WebClient
$wc.DownloadFile($url, $output)

$arguments = "/Q /T:`"$extractPath`""
$process = Start-Process -FilePath $output -ArgumentList $arguments -Wait -PassThru

$arguments = "/silent"
$process = Start-Process -FilePath $extractedFile -ArgumentList $arguments -Wait -PassThru

## Run server in gameDir

$gameDir = "C:\wreckfest-server\steamapps\common\Wreckfest Dedicated Server"
Start-Process -FilePath "$gameDir\Wreckfest_x64.exe" -ArgumentList "-s server_config.cfg" -NoNewWindow


#print out done
Write-Host "Setup completed with exit code: " $process.ExitCode