import sys
import re
import datetime

file = sys.argv[1]
fargue = file.split("\\")
fdat = fargue[-1].split(".")
filename = fdat[0]
filetype = fdat[1]
param = sys.argv[2]

e_value = 0.0
e_value_regex = re.compile("^G1_E_Value")

g1_regex = re.compile("^G1 ")

with open(sys.argv[2]) as f:
    for index, r in enumerate(f):
        matched = e_value_regex.search(r)
        if matched:
            rs = r.split('=')
            e_value = float(rs[-1])

out = open(filename+"_fixed."+filetype, 'w')
lines =  open(sys.argv[1]).readlines()

with open(sys.argv[1]) as f:
    for index, r in enumerate(f):
        matched = g1_regex.search(r)
        if matched:
            new_r = r.rstrip("\n")
            new_r += " E"+str(e_value)+"\n"
            out.write(new_r)
        else:
            out.write(r)

sys.stdout.write(filename+"_fixed."+filetype)
