gds readonly true
gds read decoded-tile.gds
load RV_K64_DECODED_TILE_00
flatten W5_DECODED_TILE_FLAT
load W5_DECODED_TILE_FLAT
extract all
ext2spice lvs
ext2spice -o decoded-tile-extracted.spice
quit -noprompt
