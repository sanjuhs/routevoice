gds readonly true
gds read {/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/taalas-array/tall-bank/r320/bank3.gds}
load TALL_BANK_R320_B03
flatten W5_TALL_BANK_FLAT
load W5_TALL_BANK_FLAT
extract all
ext2spice lvs
ext2spice -o extracted.spice
ext2spice cthresh 0
ext2spice -o extracted-cap.spice
quit -noprompt
