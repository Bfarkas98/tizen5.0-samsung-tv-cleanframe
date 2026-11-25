#!/bin/sh
set -eu
test "$(id -u)" -eq 0
test "$(dpkg --print-architecture)" = amd64
command -v lb >/dev/null

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build_dir=$(mktemp -d "${TMPDIR:-/var/tmp}/tv-os-visual.XXXXXXXX")
cd "$build_dir"
lb config --mode debian --distribution trixie --architectures amd64 \
    --binary-images iso-hybrid --debian-installer none \
    --bootappend-live "boot=live components live-config.nocomponents=lightdm persistence persistence-label=TVOS-DATA quiet"

mkdir -p config/package-lists
printf '%s\n' python3-tk lightdm lightdm-gtk-greeter xserver-xorg-core \
    xserver-xorg-input-libinput openbox dbus-x11 fonts-dejavu-core openssh-server mpv pulseaudio > config/package-lists/tv-os.list.chroot
root=config/includes.chroot
for pair in 'visual.py:opt/tv-os/visual.py' 'tv_core.py:opt/tv-os/tv_core.py' 'mpv-input.conf:opt/tv-os/mpv-input.conf' 'image/tv-os.desktop:usr/share/xsessions/tv-os.desktop' \
    'image/tv-os-lightdm.conf:etc/lightdm/lightdm.conf.d/90-tv-os.conf' \
    'examples/field-guide.json:opt/tv-os/examples/field-guide.json' 'assets/coast-at-dusk.png:opt/tv-os/assets/coast-at-dusk.png'; do
    install -Dm644 "$source_dir/${pair%%:*}" "$root/${pair#*:}"
done
install -Dm755 "$source_dir/image/start-visual-session" "$root/usr/local/bin/start-visual-session"
install -Dm755 "$source_dir/image/start-tv-ssh" "$root/usr/local/sbin/start-tv-ssh"
mkdir -p "$root/etc/systemd/system"
ln -s /dev/null "$root/etc/systemd/system/ssh.service"
ln -s /dev/null "$root/etc/systemd/system/ssh.socket"
lb build
test -s live-image-amd64.hybrid.iso
printf 'Bootable ISO: %s/live-image-amd64.hybrid.iso\n' "$build_dir"
