
import os
import sys
import socket 

if __name__=="__main__":
    
    
  

    arch =  sys.argv[1]
    model_eval =  sys.argv[2]
    hostname = socket.gethostname()

    ratio = sys.argv[3]
    print(hostname, arch, model_eval, ratio)
        
