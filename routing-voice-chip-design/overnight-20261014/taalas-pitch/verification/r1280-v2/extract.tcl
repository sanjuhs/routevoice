gds readonly true
gds read {/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/taalas-pitch/r1280-v2/bank.gds}
load PITCH_BANK_R1280
flatten W6_PITCH_BANK_FLAT
load W6_PITCH_BANK_FLAT
extract all
ext2spice lvs
ext2spice -o extracted.spice
quit -noprompt
