import sys
import re
import datetime

def extract_height(line):
    z_re = re.compile("Z[0-9.]+")
    matched = z_re.search(line)
    num = matched.group(0)[1:]
    return round(float(num), 2)

def extract_width(line):
    w_re = re.compile("W[0-9.]+")
    matched = w_re.search(line)
    num = matched.group(0)[1:]
    return round(float(num), 2)

def extract_distance(line):
    distance_re = re.compile("Distance: [0-9.]+")
    matched = distance_re.search(line)
    found = matched.group(0)
    split_found = found.split(":")
    return float(split_found[1])

#Slicing GCode input
file = sys.argv[1]
fargue = file.split("\\")
fdat = fargue[-1].split(".")
filename = fdat[0]
filetype = fdat[1]
param = sys.argv[2]

#Defining Global variables
height = 0
width = 0
acc_distance = 0
total_distance = 0
total_volume = 0
done = False

#Define Regular Expression
M221_Regex = re.compile("M221")
Distance_Regex = re.compile("Distance: ")

#Generating output file
out = open(filename+"_fixed."+filetype, 'w')

with open(sys.argv[1]) as f:
    for index, r in enumerate(f):
        matched = M221_Regex.search(r)

        #Add up current volume based on M221
        if matched:
            height = extract_height(r)
            width = extract_width(r)
            acc_volume = height * width * acc_distance
            total_volume += acc_volume
            total_distance += acc_distance
            acc_distance = 0
            continue

        matched = Distance_Regex.search(r)

        if matched:
            acc_distance += extract_distance(r)
            continue

#Add in final volume
acc_volume = height * width * acc_distance
total_distance += acc_distance
total_volume += acc_volume

with open(sys.argv[1]) as f:
    for index, r in enumerate(f):
        matched = M221_Regex.search(r)

        if matched and done == False:
            done = True
            out.write(r)
            out.write(";Total Volume / Distance of Print : "+str(round(total_volume,2))+" / "+str(round(total_distance,2))+"\n")
            continue

        out.write(r)

sys.stdout.write(filename+"_fixed."+filetype)
