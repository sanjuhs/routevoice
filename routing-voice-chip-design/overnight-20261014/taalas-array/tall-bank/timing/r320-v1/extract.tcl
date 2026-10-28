gds readonly true
gds read source-joined.gds
load TALL_ARRAY_B03_G03
flatten TALL_TIMING_ARRAY
load TALL_TIMING_ARRAY
extract all
ext2spice lvs
ext2spice -o array-lvs.spice
ext2spice cthresh 0
ext2spice -o array-cap.spice
load TALL_JOINED_R320_B03_G03
flatten TALL_TIMING_JOINED
load TALL_TIMING_JOINED
extract all
ext2spice lvs
ext2spice -o joined-lvs.spice
ext2spice cthresh 0
ext2spice -o joined-cap.spice
quit -noprompt
