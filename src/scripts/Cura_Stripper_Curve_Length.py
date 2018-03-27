import sys
import re
import datetime
import math

curve_regex = re.compile(";Curve:")
endcurve_regex = re.compile(";Curve[s]* end:")
x_re = re.compile("X[0-9.]+")
y_re = re.compile("Y[0-9.]+")
g1_regex = re.compile("G1 [A-Z0-9. ]+")
file = sys.argv[1]
fargue = file.split("\\")
fdat = fargue[-1].split(".")
filename = fdat[0]
filetype = fdat[1]
fargue[-1] = filename+"_fixed."+filetype
file = "\\".join(fargue)
curve_start = False
length_count = 0
prevx = -100
prevy = -100

out = open(filename+"_fixed."+filetype, 'w')
lines =  open(sys.argv[1]).readlines()

with open(sys.argv[1]) as f:
    for index, r in enumerate(f):
        if re.search(endcurve_regex, r) is not None:
            new_r = r.rstrip("\n")
            new_r += " Distance: "+str(round(length_count,2))+"\n"
            out.write(new_r)
            length_count = 0
            prevx = 0
            prevy = 0
        elif re.search(curve_regex, r) is not None:
            if prevx == -100 and prevy == -100:
                nextline = lines[index+1]
                xfound = x_re.search(r)
                yfound = y_re.search(r)
                if xfound is not None or yfound is not None:
                    prevx = float(xfound.group()[1:])
                    prevy = float(yfound.group()[1:])
            out.write(r)
        elif re.search(g1_regex, r) is not None:
            nextline = lines[index+1]
            xfound = x_re.search(r)
            yfound = y_re.search(r)
            if xfound is not None or yfound is not None:
                newx = float(xfound.group()[1:])
                newy = float(yfound.group()[1:])
                new_distance = round(math.sqrt((newx - prevx)**2 + (newy - prevy)**2),2)
                length_count += new_distance
                prevx = newx
                prevy = newy
                out.write(r)
                continue
            out.write(r)
        else:
            out.write(r)

sys.stdout.write(filename+"_fixed."+filetype)
