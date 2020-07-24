# Chromatic 3D Materials - Lead-In/Lead-Out Block Functionality
# Copyright 2020 - Chromatic 3D Materials - All Rights Reserved
# Author: Theresa Leibig
# Contact: tleibig@c3dm.com
# Revsions by: David Marcaccini
# Contact: dmarcaccini@c3dm.com

from LeadBlockBounding import BoundingSquare
from LeadBlockBounding import change_axis


class LeadInOutBlock:
    def __init__(self, shape="T", body_length=10, epermm=0.95):
        # Parameters of the block
        self.shape = shape
        self.body_width = 2  # mm
        self.bridge_width = 2
        self.bead_spacing = 0.5  # mm
        self.epermm = epermm
        self.body_length = body_length  # mm
        self.bridge_length = 3  # mm
        self.gap = 0  # mm
        self.speed = 1000  # mm/min

        # Corresponding gcode
        self.y_coords = None
        self.x_coords = None
        self.e_vals = None
        self.generate_gcode()

        self.bridge_bounding_square = None
        self.body_bounding_square = None
    # end __init__

    def set_shape(self, shape):
        self.shape = shape
        self.generate_gcode()
    # end set_shape

    def set_widths(self, body_width, bridge_width=2):
        self.body_width = body_width
        self.bridge_width = bridge_width
        self.generate_gcode()
    # end set_widths

    def set_bead_spacing(self, bead_spacing):
        self.bead_spacing = bead_spacing
        self.generate_gcode()
    # end set_bead_spacing

    def set_epermm(self, epermm):
        self.epermm = epermm
        self.generate_gcode()
    # end set_epermm

    def set_lengths(self, body_length, bridge_length=3):
        self.body_length = body_length
        self.bridge_length = bridge_length
        self.generate_gcode()
    # end set_lengths

    def set_gap(self, gap):
        self.gap = gap
        self.generate_gcode()
    # end set_gap

    def set_speed(self, speed):
        self.speed = speed
        self.generate_gcode()
    # end set_speed

    def generate_gcode(self):
        # finding starting x position
        x_pos = self.bridge_length + self.gap - (self.body_width % self.bead_spacing) + self.body_width
        x_pos = round(x_pos, 3)

        # finding starting y position
        if (self.body_width // self.bead_spacing) % 2 == 1:
            y_pos = 0
        else:
            y_pos = self.body_length
        # end if

        # initizing x_coord and y_coord list
        x_coords = [x_pos]
        y_coords = [y_pos]
        e_vals = [0]

        # getting gcode for the body of the block
        while x_pos > (self.bridge_length + self.gap):
            if y_pos == 0:
                y_pos = self.body_length
            else:
                y_pos = 0
            # end if
            x_coords.append(x_pos)
            y_coords.append(y_pos)
            e_vals.append(self.epermm*self.body_length)

            x_pos -= self.bead_spacing

            # Moving over in preparation for the next line.
            x_coords.append(x_pos)
            y_coords.append(y_pos)
            e_vals.append(0)
        # end while x_pos

        # Adding last vertical line.
        if y_pos == 0:
            y_pos = self.body_length
        else:
            y_pos = 0
        # end if
        x_coords.append(x_pos)
        y_coords.append(y_pos)
        e_vals.append(self.epermm * self.body_length)

        # Modifying x and y coords based on the shape of the block
        if self.shape == "T":
            for i in range(len(x_coords)):
                y_coords[i] -= (self.body_length/2 + self.bridge_length/4)
            # end for i
        elif self.shape == "L":
            for i in range(len(y_coords)):
                y_coords[i] -= self.body_length
            # end for i
        elif self.shape == "I":
            temp = list(y_coords)
            y_coords = list(x_coords)
            x_coords = list(temp)
            for i in range(len(x_coords)):
                y_coords[i] -= self.bridge_length + self.gap - (self.body_width % self.bead_spacing) + self.body_width
            # end for i
            y_coords.reverse()
        elif self.shape == "J":
            for i in range(len(y_coords)):
                y_coords[i] -= self.bridge_width
            # end for i
        # end if
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.body_bounding_square = BoundingSquare(x_coords, y_coords)

        # Reinitializing x_coords and y_coords
        x_coords = []
        y_coords = []

        if not self.shape == "I":
            if (self.bridge_width // self.bead_spacing) % 2 == 1:
                y_pos = ((self.bridge_width // self.bead_spacing) + 1) * self.bead_spacing * -1
            else:
                y_pos = (self.bridge_width // self.bead_spacing) * self.bead_spacing * -1
            # end if
            x_coords.append(x_pos)
            y_coords.append(y_pos)
            e_vals.append(0)
            while y_pos < 0:
                if x_pos == self.gap:
                    x_pos = self.bridge_length
                else:
                    x_pos = self.gap
                # end if
                x_coords.append(x_pos)
                y_coords.append(y_pos)
                e_vals.append(self.epermm*self.bridge_width)

                y_pos += self.bead_spacing

                x_coords.append(x_pos)
                y_coords.append(y_pos)
                e_vals.append(0)
            # end while y_pos
            if x_pos == self.gap:
                x_pos = self.bridge_length
            else:
                x_pos = self.gap
            # end if

            x_coords.append(x_pos)
            y_coords.append(y_pos)
            e_vals.append(self.epermm * self.bridge_width)
        # end if

        self.y_coords = self.y_coords + y_coords
        self.x_coords = self.x_coords + x_coords
        self.e_vals = e_vals
        self.bridge_bounding_square = BoundingSquare(x_coords, y_coords)
    # end generate_gcode

    def get_gcode(self):
        gcode = []
        for i in range(len(self.e_vals)):
            temp_string = "G1 X" + str(round(self.x_coords[i], 3)) + " Y" + str(round(self.y_coords[i], 3))
            if self.e_vals[i] > 0:
                temp_string = temp_string + " E" + str(self.e_vals[i])
            # end if
            if i == 0:
                temp_string = temp_string + " F" + str(self.speed)
            # end if
            temp_string = temp_string + '\n'
            gcode.append(temp_string)
        # end for i
        gcode.append('; end of lead in/out block' + '\n')
        return gcode
    # end get_gcode

    def rotate(self, theta):
        for i in range(len(self.x_coords)):
            self.x_coords[i], self.y_coords[i] = change_axis(self.x_coords[i], self.y_coords[i], theta)
        # end for i
        self.bridge_bounding_square.rotate(theta)
        self.body_bounding_square.rotate(theta)
    # end rotate

    def move(self, x, y):
        for i in range(len(self.x_coords)):
            self.x_coords[i] += x
            self.y_coords[i] += y
        # end for i
        self.bridge_bounding_square.move(x, y)
        self.body_bounding_square.move(x, y)
    # end move

    def copy(self):
        new_block = LeadInOutBlock()
        new_block.shape = self.shape
        new_block.body_width = self.body_width  # mm
        new_block.bridge_width = self.bridge_width
        new_block.bead_spacing = self.bead_spacing  # mm
        new_block.epermm = self.epermm
        new_block.body_length = self.body_length  # mm
        new_block.bridge_length = self.body_length  # mm
        new_block.gap = self.gap  # mm
        new_block.speed = self.speed  # mm/min

        # Corresponding gcode
        new_block.y_coords = list(self.y_coords)
        new_block.x_coords = list(self.x_coords)
        new_block.e_vals = list(self.e_vals)

        new_block.bridge_bounding_square = self.bridge_bounding_square.copy()
        new_block.body_bounding_square = self.body_bounding_square.copy()

        return new_block
    # end copy

# end class LeadInOutBlock
