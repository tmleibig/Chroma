import sys
import re
import datetime

def x_y_strip(command):
    x_re = re.compile("X[0-9.]+")
    y_re = re.compile("Y[--9.]+")
    command_split = command.split()
    x_match = x_re.search(command)
    y_match = y_re.search(command)
    if x_match is not None and y_match is not None:
        new_command = command_split[0]+" "+x_match.group(0)+" "+y_match.group(0)
        return new_command + "\n"
    return command

#Regex Definition
x_re = re.compile("X[0-9.]+")
y_re = re.compile("Y[--9.]+")
g1_regex = re.compile("^G1 [ A-Z0-9.-]*")
g0_regex = re.compile("^G0 [ A-Z0-9.-]*")
g0_curve_transition = re.compile("^G0 F[0-9.]+ X[0-9.]+ Y[0-9.]+ Z[0-9.]+")
g0z_regex = re.compile("^G0 Z[0-9.]+")
g1z_regex = re.compile("^G1  Z[0-9.]+")
g1zn_regex = re.compile("^G1 Z[0-9.]+")
g1fz_regex = re.compile("^G1 F[0-9.]+ Z[0-9.]+")
layer_c = re.compile("^;LAYER_COUNT:[0-9]+")
layer = re.compile("^;LAYER:[0-9][0-9]*")
M107 = re.compile("^M107")
e = re.compile("E[0-9.-]+")
type_regex = re.compile(";TYPE:[A-Za-z]+")
z_regex = re.compile("Z[0-9.]+")
m221_regex = re.compile("M221")

#Slicing GCode input
file = sys.argv[1]
fargue = file.split("\\")
fdat = fargue[-1].split(".")
filename = fdat[0]
filetype = fdat[1]
fargue[-1] = filename+"_fixed."+filetype
file = "\\".join(fargue)

#Defining global variables
chunk = "G1 Z   0.000\n"
curve_checker = False
curve_counter = 1
layer_counter = 0
code_start_flag = False
z_counter = 0
saved_r = ""
layer_start_flag = False
record_g0_layer = ""
record_g0_curve = ""
curve_length = 1
transition_move = ""
done = False
end_move = False
last_curve = False
first_curve = True
case1 = False
case1_g = ""
out_move = ""
start_layer = True

#Generating output file
out = open(filename+"_fixed."+filetype, 'w')

#Adding in detail of scripts
now = datetime.datetime.now()
out.write(";Stripped @ "+now.strftime("%Y-%m-%d %H:%M")+"\n")
out.write(";G1 Strip Version 1.0"+"\n")
lines =  open(sys.argv[1]).readlines()


with open(sys.argv[1]) as f:
    for index, r in enumerate(f):
        #Check for M221 command record it in C3DM as comment
        if re.search(m221_regex, r) is not None:
            out.write(";Cura Flow Rate Setting "+r)
        # Check for layer count
        elif re.search(layer_c,r) is not None:
            rs = r.split(":")
            rs[0] = ";Layer count"
            r = ": ".join(rs)
            out.write(r)
            code_start_flag = True
        #Check for and perform stripping at each layer
        elif re.search(layer,r) is not None:
            if layer_counter != 0:
                out.write(";Layer end: "+str(layer_counter)+"\n")
                out.write("\n"+x_y_strip(case1_g).rstrip('\n')+" ;Layer Change Transition Move\n\n")
                start_layer = False
            if record_g0_layer != "":
                record_g0_layer_split = record_g0_layer.split()
                record_g0_layer_split[0] = "G0"
                new_g0 = " ".join(record_g0_layer_split)
                out.write("\n"+x_y_strip(new_g0).rstrip('\n')+" ;Layer Change Transition Move1\n\n")
            if layer_counter == -1:
                x = lines[index+2]
                x_split = x.split()
                new_z = x_split[-1][1:]
                z_counter = float(new_z)
                record_g0 = " ".join(x_split[:-1])
            r = r.rstrip("\n")
            new_rs = r.split(":")
            new_rs[0] = ";Layer"
            new_rs[-1] = str(int(new_rs[-1])+1)
            new_r = ": ".join(new_rs)
            new_r += " @ Z"+str(z_counter)+"\n"
            out.write(new_r)
            layer_counter += 1
            curve_counter = 1
            start_layer = True
        #Simply output type
        elif re.search(type_regex,r) is not None:
            if first_curve == False:
                if curve_checker == False:
                    new_curve = ";Curve: "+str(layer_counter)+"-"+str(curve_counter)+ " @ Z"+str(z_counter)+"\n"
                    curve_checker = True
                    out.write(new_curve)
                    out.write(r)
                    continue
                if curve_checker == True:
                    if start_layer:
                        curve_checker = False


                    if case1 == True and layer_counter <= 1:
                        end_curve = ";Curve end: "+str(layer_counter)+"-"+str(curve_counter)+ " @ Z"+str(z_counter)+"\n\n"
                        curve_counter += 1
                        out.write(end_curve)
                        curve_checker = False
                        out.write(x_y_strip(case1_g).rstrip('\n')+" ;Move To\n\n")
                        case1 = False
                out.write(r)
            else:
                out.write(r)
        elif re.search(g1fz_regex,r) is not None:
            continue
        #Look for G1 with Z movement and make it G0 (Final up movement)
        elif re.search(g1z_regex,r) is not None:
            rs = r.split(" ")
            rs[0] = "G0"
            rs.remove('')
            rs[1] = "Z"+str(z_counter+5)
            r = " ".join(rs)
            out_move = r
            done = True
            end_move = True
        #Look for G1 where code has started
        elif re.search(g1_regex,r) is not None and code_start_flag:
            #Check to see if inside a curve
            if curve_checker == False:
                new_curve = ";Curve: "+str(layer_counter)+"-"+str(curve_counter)+ " @ Z"+str(z_counter)+"\n"
                curve_checker = True
                first_curve = False
                out.write(new_curve)
            new_r = x_y_strip(r)
            if re.search(g1zn_regex,r):
                continue
            out.write(new_r)
        #Look for G0 with z movement and alter z_counter
        elif re.search(g0z_regex, r) is not None and code_start_flag:
            r_split = r.split()
            new_z = r_split[-1][1:]
            z_counter = float(new_z)
        #Look for G0 with Z movement and X,Y Movement
        elif re.search(g0_regex,r) is not None and re.search(z_regex,r) is not None and re.search(x_re,r) is not None and end_move and done:
            if layer_start_flag == False:
                saved_r = r
                layer_start_flag = True
                out.write(r.rstrip("\n")+" ;Initial Move Into Print\n")
                r_split = r.split()
                new_z = r_split[-1][1:]
                z_counter = float(new_z)
                continue
            if curve_checker == True:
                end_curve = ";Curve end: "+str(layer_counter)+"-"+str(curve_counter)+ " @ Z"+str(z_counter)+"\n"
                curve_counter += 1
                out.write(end_curve)
                curve_checker = False
                record_g0 = r
            else:
                new_r = x_y_strip(r)
                out.write(new_r)
        elif re.search(g0_regex,r) is not None and re.search(z_regex,r) is not None and re.search(x_re,r) is not None:
            if layer_start_flag == False:
                saved_r = r
                layer_start_flag = True
                out.write(x_y_strip(r).rstrip("\n")+" ;Initial Move Into Print\n")
                r_split = r.split()
                new_z = r_split[-1][1:]
                z_counter = float(new_z)
                continue
            else:
                case1_g = r
                case1 = True
        #Look for simply G0 movement
        elif re.search(g0_regex,r) is not None and code_start_flag and not last_curve:
            if layer_start_flag == False:
                saved_r = r
                layer_start_flag = True
                new_r = x_y_strip(r)
                continue
            if curve_checker == True:
                end_curve = ";Curves end: "+str(layer_counter)+"-"+str(curve_counter)+ " @ Z"+str(z_counter)+"\n\n"
                curve_counter += 1
                out.write(end_curve)
                curve_checker = False
                record_g0 = r

                if end_move:
                    out.write(out_move)
                    last_curve = True
                if done == False:
                    out.write(x_y_strip(r).rstrip('\n')+" ;Move To\n\n")
            else:
                new_r = x_y_strip(r)
                out.write(new_r)

sys.stdout.write(filename+"_fixed."+filetype)
