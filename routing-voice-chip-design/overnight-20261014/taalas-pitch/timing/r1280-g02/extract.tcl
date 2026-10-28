gds readonly true
gds read source-joined.gds
load PITCH_ARRAY_R1280_G02
flatten W6_TIMING_ARRAY
load W6_TIMING_ARRAY
extract all
ext2spice lvs
ext2spice -o array-lvs.spice
ext2spice cthresh 0
ext2spice -o array-cap.spice
load PITCH_JOINED_R1280_G02
flatten W6_TIMING_JOINED
load W6_TIMING_JOINED
extract all
ext2spice lvs
ext2spice -o joined-lvs.spice
ext2spice cthresh 0
ext2spice -o joined-cap.spice
quit -noprompt
