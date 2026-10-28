import os,time,signal
# Owned PIDs of this run only; release DRC after Netgen exits to keep4active threads.
while True:
    try:os.kill(34253,0)
    except ProcessLookupError:break
    time.sleep(1)
os.kill(34317,signal.SIGCONT)
