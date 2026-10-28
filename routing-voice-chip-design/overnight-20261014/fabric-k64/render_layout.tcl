set_thread_count 1
read_db $::env(W2B_IMAGE_INPUT)
save_image -width 1600 $::env(W2B_IMAGE_OUTPUT)
exit
