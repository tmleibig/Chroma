import sys
import re
import datetime

#Slicing GCode input
file = sys.argv[1]
fargue = file.split("\\")
fdat = fargue[-1].split(".")
filename = fdat[0]
filetype = fdat[1]
param = sys.argv[2]

#Regex Definition and Global Variable Definition
p_per_nl = 0.0
p_per_nl_regex = re.compile("^Pulse Per NL")
multiplier = 0.0
multiplier_regex = re.compile("^Multiplier")
width = 0.0
width_regex = re.compile("^Width")
height = 0.0
height_regex = re.compile("^Height")

#Match parameter in PARAM file
with open(sys.argv[2]) as f:
    for index, r in enumerate(f):
        matched = p_per_nl_regex.search(r)
        if matched:
            rs = r.split('=')
            p_per_nl = float(rs[-1])
        matched = multiplier_regex.search(r)
        if matched:
            rs = r.split('=')
            multiplier = float(rs[-1])
        matched = width_regex.search(r)
        if matched:
            rs = r.split('=')
            width = float(rs[-1])
        matched = height_regex.search(r)
        if matched:
            rs = r.split('=')
            height = float(rs[-1])

#Generating output file
out = open(filename+"_fixed."+filetype, 'w')
lines =  open(sys.argv[1]).readlines()

#Add in pre_code
now = datetime.datetime.now()
out.write(";Generated @ "+now.strftime("%Y-%m-%d %H:%M")+"\n")
out.write(";Modifyied by Hyrel Code Converter Scripts (C3DM Format)\n")
out.write(";C3DM Start Code\n")
out.write("G21\t;To Millimeters\n")
out.write("G90\t;Absolute coordinates\n")
out.write("M203 X2000 Y2000 Z200\t;G0 Speed\n")
out.write("M104 S0 T12\t;Extruder Temp\n")
out.write("M140 S0\t;Bed Temp\n")
out.write("M106 S0 T12\t;Fan Speed\n")
out.write("M721 S1000 E0 P0 T12\t;Un-Prime, Speed, Pulse, Pause, Tool\n")
out.write("M722 S1000 E0 P0 T12\t;Prime, Speed, Pulse, Pause, Tool\n\n")
out.write("M756 S0.8\t;Height for FLOW calculations\n")
M221 = "M221 P"+str(p_per_nl)+" S"+str(multiplier)+" W"+str(width)+" Z"+str(height)
M221 += " T12\t;P(10) per nL, S multiplier, W width, Z height, T head\n\n"
out.write(M221)
out.write("\n;Park From\n")
out.write("G0 Z5\t\n")
out.write("G0 X240 Y10\t\n")
out.write("G0 X10 Y10\t\n\n")

#Copy the rest of the code
with open(sys.argv[1]) as f:
    for index, r in enumerate(f):
        out.write(r)

#Add in post_code
out.write("\n;Park Go To\n")
out.write("G0 X10 Y10\t;Rapid to\n")
out.write("G0 X240 Y10\t;Rapid to\n")
out.write("G0 X240 Y220\t;Rapid to Park\n\n")
out.write(";CD3M End Code\t\n")
out.write("M203 X2000 Y2000 Z200\t;G0 Speed\n")
out.write("M721 S0 E0 P0 T12\t;Un-Prime, Speed, Pulse, Pause, Tool\n")
out.write("M722 S0 E0 P0 T12\t;Prime, Speed, Pulse, Pause, Tool\n")
out.write("M103\t;Stop Extrusion\n")
out.write("M104 S0 T12\t;Extruder Temp\n")
out.write("M140 S0\t;Set Bed Temp\n")
out.write("M106 S0 T12\t;Fan Speed\n")
out.write("M18\t;Disable Motors\n")
out.write("M30\t;End of File GCODE\n")

sys.stdout.write(filename+"_fixed."+filetype)
