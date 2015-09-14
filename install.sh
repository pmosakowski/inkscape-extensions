#!/bin/bash

DEST="$HOME/.config/inkscape/extensions"

FILES=( "csv_to_vinyl.py" "csv_to_vinyl.inx" ) 

if [ ! -d "$DEST" ]; then
    mkdir -p "$DEST"
fi

for FILE in "${FILES[@]}"; do
    echo "Installing $FILE"
    cp "$FILE" "$DEST"
done
