gds readonly true
gds read tile0.gds
load RV_K64_CELL_TILE_00
flatten W5_TILE0_FLAT
load W5_TILE0_FLAT
extract all
ext2spice lvs
ext2spice -o tile0-extracted.spice
quit -noprompt
