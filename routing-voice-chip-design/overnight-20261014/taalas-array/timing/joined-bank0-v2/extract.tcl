gds readonly true
gds read input.gds
load RV_JOINED_BANK_00_0
flatten RV_JOINED_FLAT
load RV_JOINED_FLAT
extract all
ext2spice lvs
ext2spice -o joined.spice
ext2spice cthresh 0
ext2spice -o joined-cap.spice
quit -noprompt
