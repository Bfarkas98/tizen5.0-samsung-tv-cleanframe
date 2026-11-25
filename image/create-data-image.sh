#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
    echo "Usage: sh image/create-data-image.sh NEW_IMAGE_PATH" >&2
    exit 2
fi
command -v mke2fs >/dev/null
target=$1
if [ -e "$target" ] || [ -L "$target" ]; then
    echo "The output already exists." >&2
    exit 1
fi
temporary=$(mktemp -d)
image=$(mktemp "${target}.part.XXXXXXXX")
trap 'rm -rf -- "$temporary"; rm -f -- "$image"' EXIT
printf '/home\n' > "$temporary/persistence.conf"
truncate -s 512M "$image"
mke2fs -q -F -t ext4 -L TVOS-DATA -d "$temporary" "$image"
ln -- "$image" "$target"
