import sys
import re
import datetime

file = sys.argv[1]
fargue = file.split("\\")
fdat = fargue[-1].split(".")
filename = fdat[0]
filetype = fdat[1]
param = sys.argv[2]

height = 0.0
height_regex = re.compile("^Height")

f_value = 0.0
f_value_regex = re.compile("^F_Value")

e_value = 0.0
e_value_regex = re.compile("^G1_E_Value")

curve_regex = re.compile(";Curve")
found_curve = False

current_z = 0

height_indicator_regex = re.compile("@")
height_change_regex = re.compile(";Layer Change")

intial_regex = re.compile(";Initial Move Into Print")
final_z_move = re.compile(";move Z")

g1_regex = re.compile("^G1 ")

with open(sys.argv[2]) as f:
    for index, r in enumerate(f):

        matched = height_regex.search(r)
        if matched:
            rs = r.split('=')
            height = float(rs[-1])
            current_z = height

        matched = f_value_regex.search(r)
        if matched:
            rs = r.split('=')
            f_value = float(rs[-1])
        matched = e_value_regex.search(r)
        if matched:
            rs = r.split('=')
            e_value = float(rs[-1])

out = open(filename+"_fixed."+filetype, 'w')
lines =  open(sys.argv[1]).readlines()

with open(sys.argv[1]) as f:
    for index, r in enumerate(f):

        matched = final_z_move.search(r)
        if matched:
            rs = r.split(";")
            G0_split = rs[0].split(" ")
            G0_split[1] = "Z"+str(current_z+5)
            rs[0] = " ".join(G0_split)
            new_r = "; ".join(rs)
            out.write(new_r)
            continue

        matched = intial_regex.search(r)
        if matched:
            rs = r.split(";")
            rs[0] += "Z"+str(current_z)
            new_r = "; ".join(rs)
            out.write(new_r)
            continue

        matched = curve_regex.search(r)
        if matched:
            found_curve = True

        matched = g1_regex.search(r)
        if matched:
            new_r = r.rstrip("\n")
            new_r += " E"+str(e_value)+"\n"
            if found_curve:
                new_r = new_r.rstrip("\n")
                split_r = new_r.split(" ")
                split_r += ["F"+str(f_value)]
                print(split_r)
                new_r = " ".join(split_r)
                new_r += "\n"
            out.write(new_r)
            found_curve = False
            continue

        matched = height_indicator_regex.search(r)
        if matched:
            z_value = r.split("@")
            z_value[-1] = " Z"+str(current_z)
            new_r = "@".join(z_value)
            out.write(new_r+"\n")
            continue

        matched = height_change_regex.search(r)
        if matched:
            current_z += height
            current_z = round(current_z,2)
            rs = r.split(";")
            rs[0] += "Z"+str(current_z)
            new_r = " ;".join(rs)
            out.write(new_r)
            continue

        out.write(r)

sys.stdout.write(filename+"_fixed."+filetype)
