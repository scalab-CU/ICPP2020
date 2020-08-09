#!/bin/python
from string import Template



filein = open( 'runs.sh.template' )
src = Template( filein.read() )

arch="v100"
type="risky"
metric="mem_trace"
cpu_num=40


d={'arch':arch,  'type':type, 'cpu_num':cpu_num, 'metric':metric}

result = src.substitute(d)

with open("runs_%s_%s_%s.sh"%(arch,type,metric), "w+") as fileout:
    fileout.write(result)
    fileout.close()
