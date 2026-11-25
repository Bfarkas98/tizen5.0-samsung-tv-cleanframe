#!/bin/sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script with sudo inside an amd64 Debian build VM." >&2
    exit 1
fi
if [ "$(dpkg --print-architecture)" != amd64 ]; then
    echo "The build VM must use Debian amd64." >&2
    exit 1
fi
command -v lb >/dev/null

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build_dir=$(mktemp -d "${TMPDIR:-/var/tmp}/tv-os-build.XXXXXXXX")
echo "Build directory: $build_dir"
cd "$build_dir"

lb config --mode debian --distribution trixie --architectures amd64 \
    --binary-images iso-hybrid --debian-installer none \
    --bootappend-live "boot=live components quiet"

mkdir -p config/package-lists
printf '%s\n' python3 > config/package-lists/tv-os.list.chroot

root=config/includes.chroot
install -Dm644 "$source_dir/launcher.py" "$root/opt/tv-os/launcher.py"
install -Dm644 "$source_dir/image/tv-os.service" "$root/etc/systemd/system/tv-os.service"
mkdir -p "$root/etc/systemd/system/multi-user.target.wants"
ln -s ../tv-os.service "$root/etc/systemd/system/multi-user.target.wants/tv-os.service"
ln -s /dev/null "$root/etc/systemd/system/getty@tty1.service"

lb build
test -s live-image-amd64.hybrid.iso
printf 'Bootable ISO: %s/live-image-amd64.hybrid.iso\n' "$build_dir"
