gds readonly true
gds read index-array.gds
load TAALAS_MASK_INDEX_R64_C32
extract all
ext2spice lvs
ext2spice -o index-array.spice
ext2spice cthresh 0
ext2spice -o index-array-cap.spice
quit -noprompt
