#!/bin/sh
set -eu

project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y live-build

stage=$(mktemp -d /var/tmp/tv-os-source.XXXXXXXX)
cp -R "$project/image" "$project/launcher.py" "$stage/"
export TMPDIR="$stage"
sh "$stage/image/build.sh"

set -- "$stage"/tv-os-build.*/live-image-amd64.hybrid.iso
test -s "$1"
cp "$1" "$project/TV-OS-amd64.iso"
printf 'ISO saved to %s/TV-OS-amd64.iso\n' "$project"
