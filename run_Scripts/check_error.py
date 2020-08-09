import string
import subprocess
import os
import math
import re
import csv
import time
import glob
from random import shuffle
import sys
import fcntl
# ====================================== Configuration ========================================


def chk_gpu_error(node):

    # out = subprocess.check_output(['sudo', 'ssh', node, 'nvidia-smi'])
    out = subprocess.check_output(['nvidia-smi'])
    print(out.decode())
    if 'ERR!' in out.decode():
        with open(r'/home/pzou/projects/Power_Signature/Scripts/fault-nodes.lst', 'a+') as f:
            f.write(node+'\n')
        print('node {} has gpu errors'.format(node))
        
 

 

if __name__ == '__main__':
    node = sys.argv[1]
    chk_gpu_error(node)
