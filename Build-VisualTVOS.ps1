$ErrorActionPreference = 'Stop'
$projectPath = (Get-Item -LiteralPath $PSScriptRoot).FullName
$linuxPath = & wsl.exe --distribution TVOS-Linux --user root --exec wslpath -a $projectPath
if ($LASTEXITCODE -ne 0 -or -not $linuxPath) { throw 'TVOS-Linux is required in this Windows account.' }
$linuxPath = ($linuxPath | Out-String).Trim()
& wsl.exe --distribution TVOS-Linux --user root --exec sh "$linuxPath/image/build-visual-wsl.sh"
if ($LASTEXITCODE -ne 0) { throw "Graphical build failed with exit code $LASTEXITCODE." }
