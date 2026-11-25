param([Parameter(Mandatory=$true)][string]$Device)
$ErrorActionPreference = 'Stop'
$sdb = Join-Path $env:USERPROFILE '.tizen-extension-platform\server\sdktools\data\tools\sdb.exe'
if (-not (Test-Path -LiteralPath $sdb)) { throw 'Open the Tizen extension in VS Code to install the Samsung SDK tools.' }
& $sdb connect $Device
if ($LASTEXITCODE -ne 0) { throw 'Samsung developer connection failed.' }
& $sdb devices
