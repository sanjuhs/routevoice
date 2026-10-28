gds readonly true
gds read readout-tile0.gds
load RV_K64_READOUT_TILE_00
flatten W5_READOUT_TILE_FLAT
load W5_READOUT_TILE_FLAT
extract all
ext2spice lvs
ext2spice -o readout-tile0-extracted.spice
quit -noprompt
