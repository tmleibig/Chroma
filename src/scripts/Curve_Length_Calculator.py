import sys
import re
import datetime
import math

def extract_x(line):
    x_re = re.compile("X[0-9.]+")
    matched = x_re.search(line)
    num = matched.group(0)[1:]
    return round(float(num), 2)

def extract_y(line):
    y_re = re.compile("Y[0-9.]+")
    matched = y_re.search(line)
    num = matched.group(0)[1:]
    return round(float(num), 2)

#Regex Definition
curve_regex = re.compile(";Curve:")
endcurve_regex = re.compile(";Curve[s]* end:")
x_re = re.compile("X[0-9.]+")
y_re = re.compile("Y[0-9.]+")
g1_regex = re.compile("G1 [A-Z0-9. ]+")

#Slicing GCode input
file = sys.argv[1]
fargue = file.split("\\")
fdat = fargue[-1].split(".")
filename = fdat[0]
filetype = fdat[1]
fargue[-1] = filename+"_fixed."+filetype
file = "\\".join(fargue)

#Defining global variables
curve_start = False
length_count = 0
prevx = -100
prevy = -100

#Generating output file
out = open(filename+"_fixed."+filetype, 'w')
lines =  open(sys.argv[1]).readlines()

with open(sys.argv[1]) as f:
    for index, r in enumerate(f):
        # Look for end of curve and restart counter
        if re.search(endcurve_regex, r) is not None:
            new_r = r.rstrip("\n")
            new_r += " Distance: "+str(round(length_count,2))+"\n"
            out.write(new_r)
        # Look for begining of curve and start counter from next line
        elif re.search(curve_regex, r) is not None:
            length_count = 0
            prevx = -100
            prevy = -100
            out.write(r)
        # Adding new distance to counter
        elif re.search(g1_regex, r) is not None:
            nextline = lines[index+1]
            xfound = x_re.search(r)
            yfound = y_re.search(r)
            if xfound is not None and yfound is not None:
                current_x = extract_x(r)
                current_y = extract_y(r)

                next_x = x_re.search(nextline)
                next_y = y_re.search(nextline)

                if next_x is not None and next_y is not None:
                    next_x_val = extract_x(nextline)
                    next_y_val = extract_y(nextline)
                    new_distance = round(math.sqrt((next_x_val - current_x)**2 + (next_y_val - current_y)**2),2)
                    length_count += new_distance
                    out.write(r)
                    continue
                else:
                    out.write(r)
            out.write(r)
        else:
            out.write(r)

sys.stdout.write(filename+"_fixed."+filetype)
