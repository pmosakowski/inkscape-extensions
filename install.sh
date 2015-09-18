#!/bin/bash

DEST="$HOME/.config/inkscape/extensions"

FILES=( "csv_to_vinyl" 
        "fill_row" 
        "roland" ) 

if [ ! -d "$DEST" ]; then
    mkdir -p "$DEST"
fi

for FILE in "${FILES[@]}"; do
    echo "Installing $FILE"
    cp "${FILE}.inx" "$DEST"
    cp "${FILE}.py" "$DEST"
done
