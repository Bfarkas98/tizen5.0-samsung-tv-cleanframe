$ErrorActionPreference = 'Stop'
$projectPath = (Get-Item -LiteralPath $PSScriptRoot).FullName
$linuxPath = & wsl.exe --distribution TVOS-Linux --user root --exec wslpath -a $projectPath
if ($LASTEXITCODE -ne 0 -or -not $linuxPath) {
    throw 'Could not access the TVOS-Linux distribution from this Windows account.'
}
$linuxPath = ($linuxPath | Out-String).Trim()
& wsl.exe --distribution TVOS-Linux --user root --exec sh "$linuxPath/image/build-wsl.sh"
if ($LASTEXITCODE -ne 0) {
    throw "Linux build failed with exit code $LASTEXITCODE. See the output above."
}
