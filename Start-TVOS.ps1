param(
    [string]$QemuPath = $env:TVOS_QEMU_PATH,
    [ValidateSet('whpx','tcg')][string]$Accelerator = 'whpx'
)
$ErrorActionPreference = 'Stop'
if (!$QemuPath) {
    $command = Get-Command qemu-system-x86_64.exe -ErrorAction SilentlyContinue
    if (!$command) { throw 'Set TVOS_QEMU_PATH or pass -QemuPath to the QEMU executable.' }
    $QemuPath = $command.Source
}
$QemuPath = (Get-Item -LiteralPath $QemuPath).FullName
$iso = Join-Path $PSScriptRoot 'TV-OS-Appliance-amd64.iso'
$data = Join-Path $PSScriptRoot 'TVOS-Data.img'
if (!(Test-Path -LiteralPath $iso -PathType Leaf)) { throw 'The appliance ISO is missing.' }
if (!(Test-Path -LiteralPath $data -PathType Leaf)) { throw 'The writable TVOS data image is missing.' }
$argsForVm = @(
    '-machine', "pc,accel=$Accelerator", '-m', '3072', '-smp', '2',
    '-boot', 'd', '-cdrom', $iso, '-drive', "file=$data,format=raw,if=virtio",
    '-nic', 'user,model=virtio-net-pci',
    '-audiodev', 'dsound,id=tv', '-device', 'intel-hda', '-device', 'hda-output,audiodev=tv'
)
$firmware = Join-Path (Split-Path -Parent $QemuPath) 'share'
if (Test-Path -LiteralPath $firmware -PathType Container) {
    $argsForVm = @('-L', $firmware) + $argsForVm
}
& $QemuPath @argsForVm
if ($LASTEXITCODE) { throw "QEMU exited with code $LASTEXITCODE." }
