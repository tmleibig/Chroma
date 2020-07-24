#!/usr/bin/env python
# Chromatic 3D Materials - Lead-In/Lead-Out Block Functionality
# Copyright 2020 - Chromatic 3D Materials - All Rights Reserved
# Author: Theresa Leibig
# Contact: tleibig@c3dm.com
# Revsions by: David Marcaccini
# Contact: dmarcaccini@c3dm.com

import sys
import math
from LeadBlockClass import LeadInOutBlock


def read_gcode(path):
    gc_file = open(path, 'r')
    gc_lines = []
    for line in gc_file:
        gc_lines.append(line)
        # end for file
    gc_file.close()
    return gc_lines
# end read_gcode


def find_layer_beginning_and_end(gc_lines):
    layer_statistics = []
    header = True
    old_x = 0.0
    old_y = 0.0
    old_z = 0.0
    x_val = 0.0
    y_val = 0.0
    z_val = 0.0
    temp_layer_end = 0
    for i in range(len(gc_lines)):
        new_x = False
        new_y = False
        new_z = False
        new_e = False
        gc_line = str(gc_lines[i])
        s_line = gc_line.replace('\n', '').split(' ')
        if "M83" in s_line[0] or "M82" in s_line[0] or "end header" in s_line[0]:
            header = False
        elif (not header) and ("G0" in s_line[0] or "G1" in s_line[0]):
            for gcode in s_line:
                if ';' in gcode:
                    break
                elif 'X' in gcode:
                    x_val = float(gcode.strip('X'))
                    new_x = (abs(x_val - old_x) > 0.00001)
                elif 'Y' in gcode:
                    y_val = float(gcode.strip('Y'))
                    new_y = (abs(y_val - old_y) > 0.00001)
                elif 'Z' in gcode:
                    z_val = float(gcode.strip('Z'))
                    new_z = (abs(z_val - old_z) > 0.00001)
                elif "E" in gcode:
                    new_e = True
                # end if

                if not new_x:
                    x_val = old_x
                # end if
                if not new_y:
                    y_val = old_y
                # end if
                if not new_z:
                    z_val = old_z
                # end if

                if new_e and (new_x or new_y):
                    if round(z_val, 3) not in [layer[0] for layer in layer_statistics]:
                        layer_statistics.append([round(z_val, 3), i])
                        if len(layer_statistics) > 1:
                            layer_statistics[-2].append(temp_layer_end)
                        # end if
                    else:
                        temp_layer_end = i
                    # end if
                # end if

                old_x = x_val
                old_y = y_val
                old_z = z_val
            # end for gcode
        # end if
    # end for i
    layer_statistics[-1].append(temp_layer_end)
    return layer_statistics
"""
def insert_lead_in_lead_out_blocks(f_lines, layer_stats, lead_in_block, lead_out_block, overhang = False):
    print("in insert_lead_in_out blocks")
    new_f_lines = list(f_lines)
    added_lines = 0
    len_lead_out_block = 0
    len_lead_in_block = 0
    if not overhang:
        for i in range(len(layer_stats)):
            layer_height = layer_stats[i][0]
           # print(layer_stats[i])
            print(lead_in_block)
            if lead_in_block is not None:
                print("inside if lead_in_block")
                if i == 0:
                    lead_in_block = orient_block(f_lines, layer_stats[i][1], layer_stats[i][1], layer_stats[i][2], lead_in_block)
                    len_lead_in_block = len(lead_in_block.get_gcode())
                gcode = lead_in_block.get_gcode()
                new_f_lines.insert(layer_stats[i][1] + added_lines, "G1 Z" + str(layer_height) + "; beginning of lead in block \n")
                added_lines += 1
                k = 0
                print('beginning lead/in block')
                for j in range(layer_stats[i][1] + added_lines, layer_stats[i][1] + added_lines + len_lead_in_block):
                    #int(gcode[k])
                    print(gcode[k])
                    new_f_lines.insert(j, gcode[k])
                    k += 1
                added_lines += len_lead_in_block

            if lead_out_block is not None:
                if i == 0:
                    lead_out_block = orient_block(f_lines, layer_stats[i][2], layer_stats[i][1], layer_stats[i][2], lead_out_block)
                    len_lead_out_block = len(lead_out_block.get_gcode())
                gcode = lead_out_block.get_gcode()
                gcode.reverse()
                new_f_lines.insert(layer_stats[i][2] + added_lines, "G1 Z" + str(layer_height) + ";beginning of lead out block \n")
                added_lines += 1
                k = 0
                #print("begininning gcode")
                for j in range(layer_stats[i][2] + added_lines, layer_stats[i][2] + added_lines + len_lead_out_block):
                    new_f_lines.insert(j, gcode[k])
                   # print(k)
                   # print(gcode[k])
                    k += 1
                added_lines += len_lead_out_block
    return new_f_lines
"""
def insert_lead_in_lead_out_blocks(gc_lines, layer_statistics, lead_in_block, lead_out_block, overhang=False):
    new_f_lines = list(gc_lines)
    added_lines = 0
    len_lead_out_block = 0
    len_lead_in_block = 0
    if not overhang:
        for i in range(len(layer_statistics)):
            layer_height = layer_statistics[i][0]
            if lead_in_block is not None:
                if i == 0:
                    lead_in_block = orient_block(gc_lines,
                                                 layer_statistics[i][1],
                                                 layer_statistics[i][1],
                                                 layer_statistics[i][2],
                                                 lead_in_block)
                    len_lead_in_block = len(lead_in_block.get_gcode())
                # end if
                gcode = lead_in_block.get_gcode()
                new_f_lines.insert(layer_statistics[i][1] + added_lines,
                                   "G1 Z{}; beginning of lead in/out block\n".format(str(layer_height)))
                added_lines += 1
                k = 0
                for j in range(layer_statistics[i][1] + added_lines,
                               layer_statistics[i][1] + added_lines + len_lead_in_block):
                    new_f_lines.insert(j, gcode[k])
                    k += 1
                # end for j
                added_lines += len_lead_in_block
            # end if

            if lead_out_block is not None:
                if i == 0:
                    lead_out_block = orient_block(gc_lines,
                                                  layer_statistics[i][2],
                                                  layer_statistics[i][1],
                                                  layer_statistics[i][2],
                                                  lead_out_block)
                    len_lead_out_block = len(lead_out_block.get_gcode())
                # end if
                gcode = lead_out_block.get_gcode()
                gcode.reverse()
                new_f_lines.insert(layer_statistics[i][2] + added_lines,
                                   "G1 Z{};beginning of lead in/out block \n".format(str(layer_height)))
                added_lines += 1
                k = 0
                for j in range(layer_statistics[i][2] + added_lines,
                               layer_statistics[i][2] + added_lines + len_lead_out_block):
                    new_f_lines.insert(j, gcode[k])
                    k += 1
                # end for k
                added_lines += len_lead_out_block
            # end if
        # end for i
    # end if
    return new_f_lines
# end insert_lead_in_lead_out_blocks

def find_xy_pos(gc_lines, pos):
    new_x = False
    new_y = False
    x_val = 0
    y_val = 0
    gc_line = str(gc_lines[pos])
    s_line = gc_line.replace('\n', '').split(' ')
    for gcode in s_line:
        if ';' in gcode:
            break
        elif 'X' in gcode:
            x_val = float(gcode.strip('X'))
            new_x = True
        elif 'Y' in gcode:
            y_val = float(gcode.strip('Y'))
            new_y = True
        # end if
    # end for gcode
    if not (new_x and new_y):
        old_pos = find_prior_xy_pos(gc_lines, pos)
        if not new_x:
            x_val = old_pos[0]
        # end if
        if not new_y:
            y_val = old_pos[1]
        # end if
    # end if
    return x_val, y_val
# end find_xy_pos


def find_z_pos(gc_lines, pos):
    new_z = False
    z_val = 0
    gc_line = str(gc_lines[pos])
    s_line = gc_line.replace('\n', '').split(' ')
    for gcode in s_line:
        if ';' in gcode:
            break
        elif 'Z' in gcode:
            z_val = float(gcode.strip('Z'))
            new_z = True
    if not new_z:
        z_val = find_prior_z_pos(gc_lines, pos)
    return z_val
# end find_z_pos


def find_prior_xy_pos(gc_lines, pos):
    j = 1
    new_x = False
    new_y = False
    old_x_val = 0
    old_y_val = 0
    while (not new_x or not new_y) and pos > j:
        gc_line = str(gc_lines[pos - j])
        s_line = gc_line.replace('\n', '').split(' ')
        for gcode in s_line:
            if ';' in gcode:
                break
            elif 'X' in gcode:
                old_x_val = float(gcode.strip('X'))
                new_x = True
            elif 'Y' in gcode:
                old_y_val = float(gcode.strip('Y'))
                new_y = True
            # end if
        # end for gcode
        j += 1
    # end while
    return old_x_val, old_y_val
# end find_prior_xy_pos


def find_prior_z_pos(gc_lines, pos):
    j = 1
    new_z = False
    old_z_val = 0
    while (not new_z) and pos > j:
        gc_line = str(gc_lines[pos - j])
        s_line = gc_line.replace('\n', '').split(' ')
        for gcode in s_line:
            if ';' in gcode:
                break
            elif 'Z' in gcode:
                old_z_val = float(gcode.strip('X'))
                new_z = True
            # end if
        # end for gcode
        j += 1
    # end while
    return old_z_val
# end find_prior_z_pos


def is_collision(gc_lines, layer_beginning, layer_end, block):
    line_segments = []
    (x2, y2) = find_prior_xy_pos(gc_lines, layer_beginning)
    for i in range(layer_beginning, layer_end):
        (x1, y1) = (x2, y2)
        (x2, y2) = find_xy_pos(gc_lines, i)
        if block.bridge_bounding_square.inside((x1, y1), (x2, y2)):
            return True
        # end if
        line_segments.append([(x1, y1), (x2, y2)])
    # end for i
    if len(line_segments) > 0:
        for line in line_segments:
            if block.body_bounding_square.touching(line[0], line[1]):
                return True
            # end if
        # end for line
    # end if
    return False
# end if_collision

def clean_gcode(gc_lines):
    new_gc_lines = list(gc_lines)
    delete_line = False
    num_deleted = 0
    for i in range(len(gc_lines)):
        s_line = gc_lines[i].partition(';')
        #print(s_line)
        if 'beginning of lead in/out block' in s_line[2]:
            print("In beginning of lead in/out block")
            delete_line = True
        if delete_line:
            new_gc_lines.pop(i - num_deleted)
            num_deleted += 1
        if "end of lead in/out block" in s_line[2]:
            delete_line = False
    return new_gc_lines

def orient_block(gc_lines, insert_pos, layer, layer_end, block):
    x_val, y_val = find_xy_pos(gc_lines, insert_pos)
    old_x, old_y = find_prior_xy_pos(gc_lines, insert_pos)
    theta = (y_val - old_y) / math.sqrt((y_val - old_y) ** 2 + (x_val - old_x) ** 2)
    test_block = block.copy()
    test_block.rotate(theta)
    test_block.move(old_x, old_y)
    if is_collision(gc_lines, layer, layer_end, test_block):
        block.rotate(theta + math.pi)
        block.move(old_x, old_y)
        return block
    # end if
    return test_block
# end orient_block


def main(argv):
    lead_in_block = LeadInOutBlock()
    lead_in_block.set_lengths(10, 5)
    lead_in_block.set_gap(0.2)
    gc_lines = read_gcode('test.gcode')
    layer_statistics = find_layer_beginning_and_end(gc_lines)
    lead_in_block2 = lead_in_block.copy()
    gc_lines = insert_lead_in_lead_out_blocks(gc_lines, layer_statistics, lead_in_block, lead_in_block2)
    f = open('test2.gcode', 'x')
    for gc_line in gc_lines:
        f.write(gc_line)
    # end for gc_line
    f.close()
# end main


if __name__ == "__main__":
    main(sys.argv)
# end if
