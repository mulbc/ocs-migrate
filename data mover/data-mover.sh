#!/bin/bash

# Data-Mover.sh
# This script will determine if the source and target are either
# Block devices or mounted folders and either use dd or rsync to
# move the data from source to destination
# If either source or destination are neither block devices or
# mounted folders, the script will exit with an error

check_if_mount() {
    findmnt -M "$1"
}

check_if_block_device() {
    test -b "$1"
}

if (check_if_mount "/source" && check_if_mount "/destination"); then
    cd /source || exit
    # Use find & xargs to do rsync in parallel
    rsync -r . /destination
elif (check_if_block_device "/source" && check_if_block_device "/destination"); then
    rsync --sparse --copy-devices --progress /source /destination
else
    echo "ABORTING - Source and Destination are either not of the same type or neither mount or block device"
    exit 1
fi
