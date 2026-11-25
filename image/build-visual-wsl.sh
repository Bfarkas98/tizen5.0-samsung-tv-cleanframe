#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y live-build
stage=$(mktemp -d /var/tmp/tv-os-visual-source.XXXXXXXX)
cp -R "$project/image" "$project/visual.py" "$project/tv_core.py" "$project/mpv-input.conf" "$project/examples" "$project/assets" "$stage/"
export TMPDIR="$stage"
sh "$stage/image/build-visual.sh"
set -- "$stage"/tv-os-visual.*/live-image-amd64.hybrid.iso
test -s "$1"
cp "$1" "$project/TV-OS-Appliance-amd64.iso.partial"
mv "$project/TV-OS-Appliance-amd64.iso.partial" "$project/TV-OS-Appliance-amd64.iso"
printf 'ISO saved to %s/TV-OS-Appliance-amd64.iso\n' "$project"
