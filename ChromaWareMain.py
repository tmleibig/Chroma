#!/usr/bin/env python
# Chromatic 3D Materials - ChromaWare - Graphical User Interface
# Copyright 2020 - Chromatic 3D Materials - All Rights Reserved
# Author: David Marcaccini
# Contact: dmarcaccini@c3dm.com

import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.scrolledtext as tkst
from tkinter import ttk
from PIL import Image, ImageTk
import sys
import io
from contextlib import redirect_stdout
import math
from hashlib import sha256

import gcutils
import GCodeStats
import Epermm
import LeadBlock
# import LeadBlockClass
# from LeadBlock import find_layer_beginning_and_end
# from LeadBlock import insert_lead_in_lead_out_blocks


class GuiWindow(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master

        main_menu = tk.Menu(self.master)
        self.master.config(menu=main_menu)
        file_menu = tk.Menu(main_menu, tearoff=0)
        file_menu.add_command(label="Import G-Code", command=self.import_gcode)
        file_menu.add_command(label="Export G-Code", command=self.export_gcode)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)
        main_menu.add_cascade(label="File", menu=file_menu)

        self.mframe = tk.Frame(master, background="Black")
        self.mframe.pack(expand=tk.YES, fill=tk.BOTH)
        self.mframe.update()

        self.tframe = tk.Frame(self.mframe, height=60, background="#4F1595")
        tframe_logo_img_render = ImageTk.PhotoImage(Image.open("img/c3dm160x60.png"))
        tframe_logo_label = tk.Label(self.tframe, image=tframe_logo_img_render, bd=0)
        tframe_logo_label.image = tframe_logo_img_render
        tframe_logo_label.place(x=0, y=0)
        # tframe_quad_img_render = ImageTk.PhotoImage(Image.open("img/quad_30x30.png"))
        # tframe_quad_label = tk.Label(self.tframe, image=tframe_quad_img_render, bd=0)
        # tframe_quad_label.image = tframe_quad_img_render
        # tframe_quad_label.place(x=202, y=15)
        self.tframe.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

        self.bframe = tk.Frame(self.mframe, height=24)
        self.bframe.pack(after=self.tframe, side=tk.BOTTOM, expand=tk.NO, fill=tk.X)
        self.g_filename = tk.StringVar()
        self.g_file_label = tk.Label(self.bframe, textvariable=self.g_filename, relief=tk.RAISED)
        self.extrusion_mode = gcutils.ExtrusionMode.UNKNOWN
        self.g_extrusion = tk.StringVar()
        self.g_extrusion_label = tk.Label(self.bframe, textvariable=self.g_extrusion, relief=tk.RAISED)
        self.g_extrusion_convert_button_text = tk.StringVar()
        self.g_extrusion_convert_button = tk.Button(self.bframe,
                                                    textvariable=self.g_extrusion_convert_button_text,
                                                    command=self.g_extrusion_convert_button_press)
        self.g_limits_text = tk.StringVar()
        self.g_limits_label = tk.Label(self.bframe, textvariable=self.g_limits_text, relief=tk.RAISED)
        self.bframe_speed_units = tk.Frame(self.bframe,
                                           height=24,
                                           highlightbackground='#696969',
                                           highlightthickness=1,
                                           bd=0)
        self.speed_units_label = tk.Label(self.bframe_speed_units,
                                          text='Speed Units :',
                                          relief=tk.FLAT)
        self.speed_units_option = tk.StringVar(self.bframe_speed_units)
        self.speed_units_option.set('mm/sec')
        self.speed_units_options = tk.OptionMenu(self.bframe_speed_units,
                                                 self.speed_units_option,
                                                 'mm/sec',
                                                 'mm/min',
                                                 command=self.speed_unit_toggle)
        self.speed_units_label.grid(row=0, column=0)
        self.speed_units_options.grid(row=0, column=1)
        self.bframe_speed_units.pack(side=tk.RIGHT, expand=tk.NO, fill=tk.NONE)

        self.lframe = tk.Frame(self.mframe, width=40, background="Purple")
        lframe0 = tk.Frame(self.lframe, width=40, height=40)
        self.lead_blk_img_render = ImageTk.PhotoImage(Image.open("img/lead_blk_40x40.png"))
        self.lead_blk_img_render_down = ImageTk.PhotoImage(Image.open("img/lead_blk_40x40_down.png"))
        self.lead_blk_img_render_over = ImageTk.PhotoImage(Image.open("img/lead_blk_40x40_over.png"))
        self.lead_blk_button_armed = False
        self.lead_blk_label = tk.Label(lframe0, image=self.lead_blk_img_render, bd=0)
        self.lead_blk_label.place(x=0, y=0)
        self.lead_blk_label.bind("<Button-1>", self.lead_blk_button_press)
        self.lead_blk_label.bind("<ButtonRelease>", self.lead_blk_button_release)
        self.lead_blk_label.bind('<Enter>', self.lead_blk_button_enter)
        self.lead_blk_label.bind('<Leave>', self.lead_blk_button_leave)
        lframe0.grid(row=0, column=0)
        lframe1 = tk.Frame(self.lframe, width=40, height=40)
        self.shape_gen_img_render = ImageTk.PhotoImage(Image.open("img/oring_40x40.png"))
        self.shape_gen_img_render_down = ImageTk.PhotoImage(Image.open("img/oring_40x40_down.png"))
        self.shape_gen_img_render_over = ImageTk.PhotoImage(Image.open("img/oring_40x40_over.png"))
        self.shape_gen_button_armed = False
        self.shape_gen_label = tk.Label(lframe1, image=self.shape_gen_img_render, bd=0)
        self.shape_gen_label.place(x=0, y=0)
        self.shape_gen_label.bind("<Button-1>", self.shape_gen_button_press)
        self.shape_gen_label.bind("<ButtonRelease>", self.shape_gen_button_release)
        self.shape_gen_label.bind('<Enter>', self.shape_gen_button_enter)
        self.shape_gen_label.bind('<Leave>', self.shape_gen_button_leave)
        lframe1.grid(row=1, column=0)
        lframe2 = tk.Frame(self.lframe, width=40, height=40)
        self.infill_btn_img_render = ImageTk.PhotoImage(Image.open("img/infill_btn_40x40.png"))
        self.infill_btn_img_render_down = ImageTk.PhotoImage(Image.open("img/infill_btn_40x40_down.png"))
        self.infill_btn_img_render_over = ImageTk.PhotoImage(Image.open("img/infill_btn_40x40_over.png"))
        self.infill_button_armed = False
        self.infill_btn_label = tk.Label(lframe2, image=self.infill_btn_img_render, bd=0)
        self.infill_btn_label.place(x=0, y=0)
        self.infill_btn_label.bind("<Button-1>", self.infill_button_press)
        self.infill_btn_label.bind("<ButtonRelease>", self.infill_button_release)
        self.infill_btn_label.bind('<Enter>', self.infill_button_enter)
        self.infill_btn_label.bind('<Leave>', self.infill_button_leave)
        lframe2.grid(row=2, column=0)
        lframe3 = tk.Frame(self.lframe, width=40, height=40)
        self.tipwipe_img_render = ImageTk.PhotoImage(Image.open("img/tipwipe_40x40.png"))
        self.tipwipe_img_render_down = ImageTk.PhotoImage(Image.open("img/tipwipe_40x40_down.png"))
        self.tipwipe_img_render_over = ImageTk.PhotoImage(Image.open("img/tipwipe_40x40_over.png"))
        self.tipwipe_button_armed = False
        self.tipwipe_label = tk.Label(lframe3, image=self.tipwipe_img_render, bd=0)
        self.tipwipe_label.place(x=0, y=0)
        self.tipwipe_label.bind("<Button-1>", self.tipwipe_button_press)
        self.tipwipe_label.bind("<ButtonRelease>", self.tipwipe_button_release)
        self.tipwipe_label.bind('<Enter>', self.tipwipe_button_enter)
        self.tipwipe_label.bind('<Leave>', self.tipwipe_button_leave)
        lframe3.grid(row=3, column=0)
        lframe4 = tk.Frame(self.lframe, width=40, height=40)
        self.approach_img_render = ImageTk.PhotoImage(Image.open("img/approach_40x40.png"))
        self.approach_img_render_down = ImageTk.PhotoImage(Image.open("img/approach_40x40_down.png"))
        self.approach_img_render_over = ImageTk.PhotoImage(Image.open("img/approach_40x40_over.png"))
        self.approach_button_armed = False
        self.approach_label = tk.Label(lframe4, image=self.approach_img_render, bd=0)
        self.approach_label.place(x=0, y=0)
        self.approach_label.bind("<Button-1>", self.approach_button_press)
        self.approach_label.bind("<ButtonRelease>", self.approach_button_release)
        self.approach_label.bind('<Enter>', self.approach_button_enter)
        self.approach_label.bind('<Leave>', self.approach_button_leave)
        lframe4.grid(row=4, column=0)
        self.lframe.pack(after=self.bframe, side=tk.LEFT, expand=tk.NO, fill=tk.Y)

        self.rframe = tk.Frame(self.mframe, width=160, background="#DADADA")
        self.rframe.pack(after=self.lframe, side=tk.RIGHT, expand=tk.NO, fill=tk.Y)
        self.rframe.update()
        self.rframe_approach_depart_on = False
        self.rframe_approach_depart = ttk.Frame(self.rframe, width=160, height=self.rframe.winfo_height())
        self.rframe_approach_depart_selector_frame = tk.Frame(self.rframe_approach_depart, width=160)
        self.approach_depart_selection = tk.StringVar(self.rframe_approach_depart_selector_frame)
        self.approach_depart_selection.set('Approach a Stop')
        self.rframe_approach_depart_selector = tk.OptionMenu(self.rframe_approach_depart_selector_frame,
                                                             self.approach_depart_selection,
                                                             'Approach a Stop',
                                                             'Depart from a Start',
                                                             command=self.approach_depart_select_toggle)
        self.rframe_approach_depart_selector.pack(expand=tk.YES, fill=tk.BOTH)
        self.rframe_approach_canvas = tk.Canvas(self.rframe_approach_depart,
                                                width=160,
                                                height=self.rframe_approach_depart.winfo_height())
        self.rframe_depart_canvas = tk.Canvas(self.rframe_approach_depart,
                                              width=160,
                                              height=self.rframe_approach_depart.winfo_height())
        self.rframe_approach_scrollbar = ttk.Scrollbar(self.rframe_approach_depart,
                                                       orient='vertical',
                                                       command=self.rframe_approach_canvas.yview)
        self.rframe_depart_scrollbar = ttk.Scrollbar(self.rframe_approach_depart,
                                                     orient='vertical',
                                                     command=self.rframe_approach_canvas.yview)
        self.rframe_approach_scrollframe = ttk.Frame(self.rframe_approach_canvas, width=160)
        self.rframe_approach_scrollframe.bind('<Configure>',
                                              lambda e: self.rframe_approach_canvas.configure(
                                                  scrollregion=self.rframe_approach_canvas.bbox('all')
                                              ))
        self.rframe_depart_scrollframe = ttk.Frame(self.rframe_depart_canvas, width=160)
        self.rframe_depart_scrollframe.bind('<Configure>',
                                            lambda e: self.rframe_depart_canvas.configure(
                                                scrollregion=self.rframe_depart_canvas.bbox('all')
                                            ))
        self.rframe_approach_canvas.create_window((0, 0),
                                                  window=self.rframe_approach_scrollframe,
                                                  anchor='nw',
                                                  width=160)
        self.rframe_depart_canvas.create_window((0, 0),
                                                window=self.rframe_depart_scrollframe,
                                                anchor='nw',
                                                width=160)
        self.rframe_approach_canvas.configure(yscrollcommand=self.rframe_approach_scrollbar.set)
        self.rframe_depart_canvas.configure(yscrollcommand=self.rframe_depart_scrollbar.set)
        self.rframe_approach_depart_buttons = tk.Frame(self.rframe_approach_depart, width=160, background="White")
        self.rframe_approach_depart_selector_frame.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.rframe_approach_depart_buttons.pack(side=tk.BOTTOM, expand=tk.NO, fill=tk.X)

        self.rframe_approach_coast = tk.Frame(self.rframe_approach_scrollframe,
                                              width=160,
                                              background="White",
                                              highlightbackground='#696969',
                                              highlightthickness=1,
                                              bd=0)
        self.rframe_approach_coast.grid(row=0, column=0, sticky='NEWS', ipady=2, padx=1)
        self.rframe_approach_join = tk.Frame(self.rframe_approach_scrollframe,
                                             width=160,
                                             background="White",
                                             highlightbackground='#696969',
                                             highlightthickness=1,
                                             bd=0)
        self.rframe_approach_join.grid(row=1, column=0, sticky='NEWS', ipady=2, padx=1)
        self.rframe_approach_leadout = tk.Frame(self.rframe_approach_scrollframe,
                                                width=160,
                                                background="White",
                                                highlightbackground='#696969',
                                                highlightthickness=1,
                                                bd=0)
        self.rframe_approach_leadout.grid(row=2, column=0, sticky='NEWS', ipady=2, padx=1)

        self.rframe_depart_initial = tk.Frame(self.rframe_depart_scrollframe,
                                              width=160,
                                              background="White",
                                              highlightbackground='#696969',
                                              highlightthickness=1,
                                              bd=0)
        self.rframe_depart_initial.grid(row=0, column=0, sticky='NEWS', ipady=2, padx=1)
        self.rframe_depart_secondary = tk.Frame(self.rframe_depart_scrollframe,
                                                width=160,
                                                background="White",
                                                highlightbackground='#696969',
                                                highlightthickness=1,
                                                bd=0)
        self.rframe_depart_secondary.grid(row=1, column=0, sticky='NEWS', ipady=2, padx=1)
        self.rframe_depart_standard = tk.Frame(self.rframe_depart_scrollframe,
                                               width=160,
                                               background="White",
                                               highlightbackground='#696969',
                                               highlightthickness=1,
                                               bd=0)
        self.rframe_depart_standard.grid(row=2, column=0, sticky='NEWS', ipady=2, padx=1)

        self.approach_coast_start_sentinel_label = tk.Label(self.rframe_approach_coast,
                                                            text='Coast Start Sentinel:',
                                                            background='White')
        self.approach_coast_start_sentinel_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.approach_coast_start_sentinel_entry = tk.Entry(self.rframe_approach_coast, bd=3)
        self.approach_coast_start_sentinel_entry.grid(row=1, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_coast_end_sentinel_label = tk.Label(self.rframe_approach_coast,
                                                          text='Coast End Sentinel:',
                                                          background='White')
        self.approach_coast_end_sentinel_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.approach_coast_end_sentinel_entry = tk.Entry(self.rframe_approach_coast, bd=3)
        self.approach_coast_end_sentinel_entry.grid(row=3, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_coast_speed_entry_text = tk.StringVar(self.rframe_approach_coast)
        self.approach_coast_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.approach_coast_speed_label = tk.Label(self.rframe_approach_coast,
                                                   textvariable=self.approach_coast_speed_entry_text,
                                                   background='White')
        self.approach_coast_speed_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.approach_coast_speed_entry = tk.Entry(self.rframe_approach_coast, bd=3)
        self.approach_coast_speed_entry.grid(row=5, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_coast_speed_gcmd_label = tk.Label(self.rframe_approach_coast,
                                                        text='Apply new speed to:',
                                                        background='White')
        self.approach_coast_speed_gcmd_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.approach_coast_speed_g0_enable = tk.BooleanVar()
        self.approach_coast_speed_g0_cb = tk.Checkbutton(self.rframe_approach_coast,
                                                         text='G0',
                                                         variable=self.approach_coast_speed_g0_enable,
                                                         onvalue=tk.TRUE,
                                                         offvalue=tk.FALSE,
                                                         background='White')
        self.approach_coast_speed_g0_cb.grid(row=7, column=0, sticky=tk.W)
        self.approach_coast_speed_g1_enable = tk.BooleanVar(value=tk.TRUE)
        self.approach_coast_speed_g1_cb = tk.Checkbutton(self.rframe_approach_coast,
                                                         text='G1',
                                                         variable=self.approach_coast_speed_g1_enable,
                                                         onvalue=tk.TRUE,
                                                         offvalue=tk.FALSE,
                                                         background='White')
        self.approach_coast_speed_g1_cb.grid(row=7, column=1, sticky=tk.E)
        self.approach_coast_e_value_label = tk.Label(self.rframe_approach_coast, text='Coast E/mm:',
                                                     background='White')
        self.approach_coast_e_value_label.grid(row=8, column=0, columnspan=2, sticky=tk.W)
        self.approach_coast_e_value_entry = tk.Entry(self.rframe_approach_coast, bd=3)
        self.approach_coast_e_value_entry.grid(row=9, column=0, columnspan=2, sticky='WE', padx=1)

        self.approach_join_start_sentinel_label = tk.Label(self.rframe_approach_join, text='Join Start Sentinel:',
                                                           background='White')
        self.approach_join_start_sentinel_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.approach_join_start_sentinel_entry = tk.Entry(self.rframe_approach_join, bd=3)
        self.approach_join_start_sentinel_entry.grid(row=1, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_join_end_sentinel_label = tk.Label(self.rframe_approach_join, text='Join End Sentinel:',
                                                         background='White')
        self.approach_join_end_sentinel_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.approach_join_end_sentinel_entry = tk.Entry(self.rframe_approach_join, bd=3)
        self.approach_join_end_sentinel_entry.grid(row=3, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_join_speed_entry_text = tk.StringVar(self.rframe_approach_join)
        self.approach_join_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.approach_join_speed_label = tk.Label(self.rframe_approach_join,
                                                  textvariable=self.approach_join_speed_entry_text,
                                                  background='White')
        self.approach_join_speed_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.approach_join_speed_entry = tk.Entry(self.rframe_approach_join, bd=3)
        self.approach_join_speed_entry.grid(row=5, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_join_speed_gcmd_label = tk.Label(self.rframe_approach_join, text='Apply new speed to:',
                                                       background='White')
        self.approach_join_speed_gcmd_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.approach_join_speed_g0_enable = tk.BooleanVar()
        self.approach_join_speed_g0_cb = tk.Checkbutton(self.rframe_approach_join,
                                                        text='G0',
                                                        variable=self.approach_join_speed_g0_enable,
                                                        onvalue=tk.TRUE,
                                                        offvalue=tk.FALSE,
                                                        background='White')
        self.approach_join_speed_g0_cb.grid(row=7, column=0, sticky=tk.W)
        self.approach_join_speed_g1_enable = tk.BooleanVar(value=tk.TRUE)
        self.approach_join_speed_g1_cb = tk.Checkbutton(self.rframe_approach_join,
                                                        text='G1',
                                                        variable=self.approach_join_speed_g1_enable,
                                                        onvalue=tk.TRUE,
                                                        offvalue=tk.FALSE,
                                                        background='White')
        self.approach_join_speed_g1_cb.grid(row=7, column=1, sticky=tk.E)
        self.approach_join_e_value_label = tk.Label(self.rframe_approach_join, text='Join E/mm:',
                                                    background='White')
        self.approach_join_e_value_label.grid(row=8, column=0, columnspan=2, sticky=tk.W)
        self.approach_join_e_value_entry = tk.Entry(self.rframe_approach_join, bd=3)
        self.approach_join_e_value_entry.grid(row=9, column=0, columnspan=2, sticky='WE', padx=1)

        self.approach_leadout_start_sentinel_label = tk.Label(self.rframe_approach_leadout,
                                                              text='Leadout Start Sentinel:',
                                                              background='White')
        self.approach_leadout_start_sentinel_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.approach_leadout_start_sentinel_entry = tk.Entry(self.rframe_approach_leadout, bd=3)
        self.approach_leadout_start_sentinel_entry.grid(row=1, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_leadout_end_sentinel_label = tk.Label(self.rframe_approach_leadout,
                                                            text='Leadout End Sentinel:',
                                                            background='White')
        self.approach_leadout_end_sentinel_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.approach_leadout_end_sentinel_entry = tk.Entry(self.rframe_approach_leadout, bd=3)
        self.approach_leadout_end_sentinel_entry.grid(row=3, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_leadout_speed_entry_text = tk.StringVar(self.rframe_approach_join)
        self.approach_leadout_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.approach_leadout_speed_label = tk.Label(self.rframe_approach_leadout,
                                                     textvariable=self.approach_leadout_speed_entry_text,
                                                     background='White')
        self.approach_leadout_speed_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.approach_leadout_speed_entry = tk.Entry(self.rframe_approach_leadout, bd=3)
        self.approach_leadout_speed_entry.grid(row=5, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_leadout_speed_gcmd_label = tk.Label(self.rframe_approach_leadout, text='Apply new speed to:',
                                                          background='White')
        self.approach_leadout_speed_gcmd_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.approach_leadout_speed_g0_enable = tk.BooleanVar()
        self.approach_leadout_speed_g0_cb = tk.Checkbutton(self.rframe_approach_leadout,
                                                           text='G0',
                                                           variable=self.approach_leadout_speed_g0_enable,
                                                           onvalue=tk.TRUE,
                                                           offvalue=tk.FALSE,
                                                           background='White')
        self.approach_leadout_speed_g0_cb.grid(row=7, column=0, sticky=tk.W)
        self.approach_leadout_speed_g1_enable = tk.BooleanVar(value=tk.TRUE)
        self.approach_leadout_speed_g1_cb = tk.Checkbutton(self.rframe_approach_leadout,
                                                           text='G1',
                                                           variable=self.approach_leadout_speed_g1_enable,
                                                           onvalue=tk.TRUE,
                                                           offvalue=tk.FALSE,
                                                           background='White')
        self.approach_leadout_speed_g1_cb.grid(row=7, column=1, sticky=tk.E)
        self.approach_leadout_e_value_label = tk.Label(self.rframe_approach_leadout, text='Leadout E/mm:',
                                                       background='White')
        self.approach_leadout_e_value_label.grid(row=8, column=0, columnspan=2, sticky=tk.W)
        self.approach_leadout_e_value_entry = tk.Entry(self.rframe_approach_leadout, bd=3)
        self.approach_leadout_e_value_entry.grid(row=9, column=0, columnspan=2, sticky='WE', padx=1)
        self.approach_leadout_z_value_label = tk.Label(self.rframe_approach_leadout, text='Leadout Z Lift (mm):',
                                                       background='White')
        self.approach_leadout_z_value_label.grid(row=10, column=0, columnspan=2, sticky=tk.W)
        self.approach_leadout_z_value_entry = tk.Entry(self.rframe_approach_leadout, bd=3)
        self.approach_leadout_z_value_entry.grid(row=11, column=0, columnspan=2, sticky='WE', padx=1)

        self.depart_initial_start_sentinel_label = tk.Label(self.rframe_depart_initial,
                                                            text='Initial Start Sentinel:',
                                                            background='White')
        self.depart_initial_start_sentinel_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.depart_initial_start_sentinel_entry = tk.Entry(self.rframe_depart_initial, bd=3)
        self.depart_initial_start_sentinel_entry.grid(row=1, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_initial_end_sentinel_label = tk.Label(self.rframe_depart_initial,
                                                          text='Initial End Sentinel:',
                                                          background='White')
        self.depart_initial_end_sentinel_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.depart_initial_end_sentinel_entry = tk.Entry(self.rframe_depart_initial, bd=3)
        self.depart_initial_end_sentinel_entry.grid(row=3, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_initial_speed_entry_text = tk.StringVar(self.rframe_depart_initial)
        self.depart_initial_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.depart_initial_speed_label = tk.Label(self.rframe_depart_initial,
                                                   textvariable=self.depart_initial_speed_entry_text,
                                                   background='White')
        self.depart_initial_speed_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.depart_initial_speed_entry = tk.Entry(self.rframe_depart_initial, bd=3)
        self.depart_initial_speed_entry.grid(row=5, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_initial_speed_gcmd_label = tk.Label(self.rframe_depart_initial,
                                                        text='Apply new speed to:',
                                                        background='White')
        self.depart_initial_speed_gcmd_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.depart_initial_speed_g0_enable = tk.BooleanVar()
        self.depart_initial_speed_g0_cb = tk.Checkbutton(self.rframe_depart_initial,
                                                         text='G0',
                                                         variable=self.depart_initial_speed_g0_enable,
                                                         onvalue=tk.TRUE,
                                                         offvalue=tk.FALSE,
                                                         background='White')
        self.depart_initial_speed_g0_cb.grid(row=7, column=0, sticky=tk.W)
        self.depart_initial_speed_g1_enable = tk.BooleanVar(value=tk.TRUE)
        self.depart_initial_speed_g1_cb = tk.Checkbutton(self.rframe_depart_initial,
                                                         text='G1',
                                                         variable=self.depart_initial_speed_g1_enable,
                                                         onvalue=tk.TRUE,
                                                         offvalue=tk.FALSE,
                                                         background='White')
        self.depart_initial_speed_g1_cb.grid(row=7, column=1, sticky=tk.E)
        self.depart_initial_e_value_label = tk.Label(self.rframe_depart_initial,
                                                     text='Initial E/mm:',
                                                     background='White')
        self.depart_initial_e_value_label.grid(row=8, column=0, columnspan=2, sticky=tk.W)
        self.depart_initial_e_value_entry = tk.Entry(self.rframe_depart_initial, bd=3)
        self.depart_initial_e_value_entry.grid(row=9, column=0, columnspan=2, sticky='WE', padx=1)

        self.depart_secondary_start_sentinel_label = tk.Label(self.rframe_depart_secondary,
                                                              text='Secondary Start Sentinel:',
                                                              background='White')
        self.depart_secondary_start_sentinel_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.depart_secondary_start_sentinel_entry = tk.Entry(self.rframe_depart_secondary, bd=3)
        self.depart_secondary_start_sentinel_entry.grid(row=1, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_secondary_end_sentinel_label = tk.Label(self.rframe_depart_secondary,
                                                            text='Secondary End Sentinel:',
                                                            background='White')
        self.depart_secondary_end_sentinel_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.depart_secondary_end_sentinel_entry = tk.Entry(self.rframe_depart_secondary, bd=3)
        self.depart_secondary_end_sentinel_entry.grid(row=3, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_secondary_speed_entry_text = tk.StringVar(self.rframe_depart_secondary)
        self.depart_secondary_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.depart_secondary_speed_label = tk.Label(self.rframe_depart_secondary,
                                                     textvariable=self.depart_secondary_speed_entry_text,
                                                     background='White')
        self.depart_secondary_speed_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.depart_secondary_speed_entry = tk.Entry(self.rframe_depart_secondary, bd=3, width=1)
        self.depart_secondary_speed_entry.grid(row=5, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_secondary_speed_gcmd_label = tk.Label(self.rframe_depart_secondary,
                                                          text='Apply new speed to:',
                                                          background='White')
        self.depart_secondary_speed_gcmd_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.depart_secondary_speed_g0_enable = tk.BooleanVar()
        self.depart_secondary_speed_g0_cb = tk.Checkbutton(self.rframe_depart_secondary,
                                                           text='G0',
                                                           variable=self.depart_secondary_speed_g0_enable,
                                                           onvalue=tk.TRUE,
                                                           offvalue=tk.FALSE,
                                                           background='White')
        self.depart_secondary_speed_g0_cb.grid(row=7, column=0, sticky=tk.W)
        self.depart_secondary_speed_g1_enable = tk.BooleanVar(value=tk.TRUE)
        self.depart_secondary_speed_g1_cb = tk.Checkbutton(self.rframe_depart_secondary,
                                                           text='G1',
                                                           variable=self.depart_secondary_speed_g1_enable,
                                                           onvalue=tk.TRUE,
                                                           offvalue=tk.FALSE,
                                                           background='White')
        self.depart_secondary_speed_g1_cb.grid(row=7, column=1, sticky=tk.E)
        self.depart_secondary_e_value_label = tk.Label(self.rframe_depart_secondary,
                                                       text='Secondary E/mm:',
                                                       background='White')
        self.depart_secondary_e_value_label.grid(row=8, column=0, columnspan=2, sticky=tk.W)
        self.depart_secondary_e_value_entry = tk.Entry(self.rframe_depart_secondary, bd=3)
        self.depart_secondary_e_value_entry.grid(row=9, column=0, columnspan=2, sticky='WE', padx=1)

        self.depart_standard_start_sentinel_label = tk.Label(self.rframe_depart_standard,
                                                             text='Standard Start Sentinel:',
                                                             background='White')
        self.depart_standard_start_sentinel_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.depart_standard_start_sentinel_entry = tk.Entry(self.rframe_depart_standard, bd=3)
        self.depart_standard_start_sentinel_entry.grid(row=1, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_standard_end_sentinel_label = tk.Label(self.rframe_depart_standard,
                                                           text='Standard End Sentinel:',
                                                           background='White')
        self.depart_standard_end_sentinel_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.depart_standard_end_sentinel_entry = tk.Entry(self.rframe_depart_standard, bd=3)
        self.depart_standard_end_sentinel_entry.grid(row=3, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_standard_speed_entry_text = tk.StringVar(self.rframe_depart_standard)
        self.depart_standard_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.depart_standard_speed_label = tk.Label(self.rframe_depart_standard,
                                                    textvariable=self.depart_standard_speed_entry_text,
                                                    background='White')
        self.depart_standard_speed_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.depart_standard_speed_entry = tk.Entry(self.rframe_depart_standard, bd=3)
        self.depart_standard_speed_entry.grid(row=5, column=0, columnspan=2, sticky='WE', padx=1)
        self.depart_standard_speed_gcmd_label = tk.Label(self.rframe_depart_standard,
                                                         text='Apply new speed to:',
                                                         background='White')
        self.depart_standard_speed_gcmd_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.depart_standard_speed_g0_enable = tk.BooleanVar()
        self.depart_standard_speed_g0_cb = tk.Checkbutton(self.rframe_depart_standard,
                                                          text='G0',
                                                          variable=self.depart_standard_speed_g0_enable,
                                                          onvalue=tk.TRUE,
                                                          offvalue=tk.FALSE,
                                                          background='White')
        self.depart_standard_speed_g0_cb.grid(row=7, column=0, sticky=tk.W)
        self.depart_standard_speed_g1_enable = tk.BooleanVar(value=tk.TRUE)
        self.depart_standard_speed_g1_cb = tk.Checkbutton(self.rframe_depart_standard,
                                                          text='G1',
                                                          variable=self.depart_standard_speed_g1_enable,
                                                          onvalue=tk.TRUE,
                                                          offvalue=tk.FALSE,
                                                          background='White')
        self.depart_standard_speed_g1_cb.grid(row=7, column=1, sticky=tk.E)
        self.depart_standard_e_value_label = tk.Label(self.rframe_depart_standard,
                                                      text='Standard E/mm:',
                                                      background='White')
        self.depart_standard_e_value_label.grid(row=8, column=0, columnspan=2, sticky=tk.W)
        self.depart_standard_e_value_entry = tk.Entry(self.rframe_depart_standard, bd=3)
        self.depart_standard_e_value_entry.grid(row=9, column=0, columnspan=2, sticky='WE', padx=1)

        self.approach_depart_apply_button = tk.Button(self.rframe_approach_depart_buttons,
                                                      text='Apply Settings',
                                                      command=self.approach_depart_apply)
        self.approach_depart_apply_button.grid(row=0, column=0, ipadx=6, sticky='WE')
        self.approach_depart_reset_button = tk.Button(self.rframe_approach_depart_buttons,
                                                      text='Reset',
                                                      command=self.approach_depart_apply)  # TODO change me to reset
        self.approach_depart_reset_button.grid(row=0, column=1, ipadx=12, sticky='WE')

        #lead block set up
        #Setting up the selection menu
        self.rframe_lead_blk_on = False
        self.rframe_in_out = ttk.Frame(self.rframe, width=160, height=self.rframe.winfo_height())
        self.rframe_in_out_selector_frame = tk.Frame(self.rframe_in_out, width=160)
        self.in_out_selection = tk.StringVar(self.rframe_in_out_selector_frame)
        self.in_out_selection.set('Lead In Block')
        self.rframe_in_out_selector = tk.OptionMenu(self.rframe_in_out_selector_frame,
                                                             self.in_out_selection,
                                                             'Lead In Block',
                                                             'Lead Out Block',
                                                             command=self.in_out_select_toggle)

        self.rframe_in_out_selector_frame.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.rframe_in_out_selector.pack(expand=tk.YES, fill=tk.BOTH)
        # Setting up Canvas

        self.rframe_lead_in_canvas = tk.Canvas(self.rframe_in_out,
                                                width=160,
                                                height=self.rframe_in_out.winfo_height())
        self.rframe_lead_out_canvas = tk.Canvas(self.rframe_in_out,
                                              width=160,
                                              height=self.rframe_in_out.winfo_height())
        self.rframe_lead_in_scrollbar = ttk.Scrollbar(self.rframe_in_out,
                                                       orient='vertical',
                                                       command=self.rframe_approach_canvas.yview)
        self.rframe_lead_out_scrollbar = ttk.Scrollbar(self.rframe_in_out,
                                                     orient='vertical',
                                                     command=self.rframe_lead_out_canvas.yview)
        self.rframe_lead_in_scrollframe = ttk.Frame(self.rframe_lead_in_canvas, width=160)
        self.rframe_lead_in_scrollframe.bind('<Configure>',
                                              lambda e: self.rframe_lead_in_canvas.configure(
                                                  scrollregion=self.rframe_lead_in_canvas.bbox('all')
                                              ))
        self.rframe_lead_out_scrollframe = ttk.Frame(self.rframe_lead_out_canvas, width=160)
        self.rframe_lead_out_scrollframe.bind('<Configure>',
                                            lambda e: self.rframe_lead_out_canvas.configure(
                                                scrollregion=self.rframe_lead_out_canvas.bbox('all')
                                            ))
        self.rframe_lead_in_canvas.create_window((0, 0),
                                                  window=self.rframe_lead_in_scrollframe,
                                                  anchor='nw',
                                                  width=160)
        self.rframe_lead_out_canvas.create_window((0, 0),
                                                window=self.rframe_lead_out_scrollframe,
                                                anchor='nw',
                                                width=160)
        self.rframe_lead_in_canvas.configure(yscrollcommand=self.rframe_lead_in_scrollbar.set)
        self.rframe_lead_out_canvas.configure(yscrollcommand=self.rframe_lead_out_scrollbar.set)
        # Setting "Insert Lead in/out Button
        self.add_lead_in = tk.BooleanVar()
        self.add_lead_out = tk.BooleanVar()
        self.add_lead_in.set(False)
        self.add_lead_in.set(False)
        self.add_lead_in_button = tk.Checkbutton(self.rframe_lead_in_canvas,
                                                          text='Insert Lead In Block',
                                                          variable= self.add_lead_in,
                                                          onvalue=tk.TRUE,
                                                          offvalue=tk.FALSE)
        self.add_lead_in_button.grid(row = 1, column = 0)
        self.add_lead_out_button = tk.Checkbutton(self.rframe_lead_out_canvas,
                                                            text ='Insert Lead Out Block',
                                                            variable = self.add_lead_out,
                                                            onvalue = tk.TRUE,
                                                            offvalue =tk.FALSE)
        self.add_lead_out_button.grid(row = 1, column = 0)
        # Setting lead in shape
        self.lead_in_shape_label = tk.Label(self.rframe_lead_in_canvas, text = "Select Block Shape")
        self.lead_in_shape_label.grid(row = 2, column = 0, columnspan = 2)
        self.lead_in_shape_selection = tk.StringVar(self.rframe_lead_in_canvas)
        self.lead_in_shape_selection.set('T')
        self.lead_in_shape_selector = tk.OptionMenu(self.rframe_lead_in_canvas,
                                                    self.lead_in_shape_selection,
                                                    'T','J', 'L', 'I')
        self.lead_in_shape_selector.grid(row = 3, column = 0, columnspan = 1)

        # Setting lead out shape
        self.lead_out_shape_label = tk.Label(self.rframe_lead_out_canvas, text="Select Block Shape")
        self.lead_out_shape_label.grid(row=2, column=0, columnspan=2)
        self.lead_out_shape_selection = tk.StringVar(self.rframe_lead_out_canvas)
        self.lead_out_shape_selection.set('T')
        self.lead_out_shape_selector = tk.OptionMenu(self.rframe_lead_out_canvas,
                                                    self.lead_out_shape_selection,
                                                    'T', 'J', 'L', 'I')
        self.lead_out_shape_selector.grid(row=3, column=0, columnspan=1)

        #Adding Block Dimensions
        self.in_block_length_label = tk.Label(self.rframe_lead_in_canvas, text= "Block Length: ")
        self.in_block_length_label.grid(row = 4, column = 0)
        self.in_block_length = tk.Entry(self.rframe_lead_in_canvas, bd = 3)
        self.in_block_length.insert(0, string ='10')
        self.in_block_length.grid(row = 5, column = 0)
        self.in_block_length_units_label = tk.Label(self.rframe_lead_in_canvas, text = "mm")
        self.in_block_length_units_label.grid(row = 5, column = 1)

        self.in_block_width_label = tk.Label(self.rframe_lead_in_canvas, text = "Block Width:")
        self.in_block_width_label.grid(row = 6, column = 0)
        self.in_block_width = tk.Entry(self.rframe_lead_in_canvas, bd = 2)
        self.in_block_width.insert(0, string= '2')
        self.in_block_width.grid(row = 7, column = 0)
        self.in_block_width_units_label = tk.Label(self.rframe_lead_in_canvas, text = "mm")
        self.in_block_width_units_label.grid(row = 7, column = 1)

        self.out_block_length_label = tk.Label(self.rframe_lead_out_canvas, text= "Block Length: ")
        self.out_block_length_label.grid(row = 4, column = 0)
        self.out_block_length = tk.Entry(self.rframe_lead_out_canvas, bd = 3)
        self.out_block_length.insert(0, string ='10')
        self.out_block_length.grid(row = 5, column = 0)
        self.out_block_length_units_label = tk.Label(self.rframe_lead_out_canvas, text = "mm")
        self.out_block_length_units_label.grid(row = 5, column = 1)

        self.out_block_width_label = tk.Label(self.rframe_lead_out_canvas, text = "Block Width:")
        self.out_block_width_label.grid(row = 6, column = 0)
        self.out_block_width = tk.Entry(self.rframe_lead_out_canvas, bd = 3)
        self.out_block_width.insert(0, string= '2')
        self.out_block_width.grid(row = 7, column = 0)
        self.out_block_width_units_label = tk.Label(self.rframe_lead_out_canvas, text = "mm")
        self.out_block_width_units_label.grid(row = 7, column = 1)

        #Setting bead Spacing
        self.in_block_bead_spacing_label = tk.Label(self.rframe_lead_in_canvas, text = "Bead Spacing:")
        self.in_block_bead_spacing_label.grid(row = 8, column = 0)
        self.in_block_bead_spacing = tk.Entry(self.rframe_lead_in_canvas, bd = 3)
        self.in_block_bead_spacing.insert(0, '0.5')
        self.in_block_bead_spacing.grid(row = 9, column =0)
        self.in_block_bead_spacing_units = tk.Label(self.rframe_lead_in_canvas, text = 'mm')
        self.in_block_bead_spacing_units.grid(row = 9, column = 1)

        self.out_block_bead_spacing_label = tk.Label(self.rframe_lead_out_canvas, text="Bead Spacing:")
        self.out_block_bead_spacing_label.grid(row=8, column=0)
        self.out_block_bead_spacing = tk.Entry(self.rframe_lead_out_canvas, bd=3)
        self.out_block_bead_spacing.insert(0, '0.5')
        self.out_block_bead_spacing.grid(row=9, column=0)
        self.out_block_bead_spacing_units = tk.Label(self.rframe_lead_out_canvas, text='mm')
        self.out_block_bead_spacing_units.grid(row=9, column=1)

        #Setting Epermm

        self.in_block_epermm_label = tk.Label(self.rframe_lead_in_canvas, text = 'E/mm')
        self.in_block_epermm_label.grid(row=10, column = 0)
        self.in_block_epermm = tk.Entry(self.rframe_lead_in_canvas, bd = 3)
        self.in_block_epermm.insert(0, '0.95')
        self.in_block_epermm.grid(row = 11, column = 0)

        self.out_block_epermm_label = tk.Label(self.rframe_lead_out_canvas, text='E/mm')
        self.out_block_epermm_label.grid(row=10, column=0)
        self.out_block_epermm = tk.Entry(self.rframe_lead_out_canvas, bd=3)
        self.out_block_epermm.insert(0, '0.95')
        self.out_block_epermm.grid(row=11, column=0)

        self.rframe_in_out_buttons = tk.Frame(self.rframe_in_out, width=160, background="White")
        self.rframe_in_out_buttons.pack(side=tk.BOTTOM, expand=tk.NO, fill=tk.X)
        self.lead_blk_apply_button = tk.Button(self.rframe_in_out_buttons,
                                                      text='Apply Settings',
                                                      command=self.lead_blk_apply)
        self.lead_blk_apply_button.grid(row=0, column=0, ipadx=6, sticky='WE')
        self.lead_blk_reset_button = tk.Button(self.rframe_in_out_buttons,
                                                      text='Reset',
                                                      command=self.lead_blk_apply)  # TODO change me to reset
        self.lead_blk_reset_button.grid(row=0, column=1, ipadx=12, sticky='WE')


        self.gframe_layout = "<DoubleVertical>"
        # self.gframe_layout = "<Quad>"
        self.gframe = tk.Frame(self.mframe, background="Black")
        self.gframe.pack(after=self.rframe, side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.gframe.update()
        self.gframe0 = tk.Frame(self.gframe, background="Black")
        self.gframe1 = tk.Frame(self.gframe, background="Black")
        self.gframe2 = tk.Frame(self.gframe, background="Black")
        self.gframe3 = tk.Frame(self.gframe, background="Black")
        self.e_per_mm_field_label = tk.Label(self.gframe1, text='Desired E/mm:', bd=0)
        self.e_per_mm_field_entry = tk.Entry(self.gframe1, bd=3)
        self.e_per_mm_field_entry.insert(0, str(Epermm.get_default_e_per_mm()))
        self.e_per_mm_button = tk.Button(self.gframe1, text='Revise E/mm', command=self.epermm_button_press)
        self.gcanvas = tk.Canvas(self.gframe2, bd=0, highlightthickness=0, background="Black")
        self.gframe_setup()
        self.draw_gcanvas([])

        self.gcode_scrollable_txt = tkst.ScrolledText(self.gframe0, wrap=tk.WORD)
        self.gcode_open_filename = None

        self.gcode_stats = tk.Label(self.gframe1, justify=tk.LEFT, bd=1)

        self.gframe.bind("<Configure>", self.on_resize)

    # end __init__

    def rframe_approach_depart_setup(self):
        if self.rframe_approach_depart_on is True:
            if self.approach_depart_selection.get() == 'Approach a Stop':
                self.rframe_depart_canvas.pack_forget()
                self.rframe_depart_scrollbar.pack_forget()
                self.rframe_approach_canvas.pack(side=tk.LEFT,
                                                 expand=tk.YES,
                                                 fill=tk.BOTH,
                                                 after=self.rframe_approach_depart_buttons)
                self.rframe_approach_scrollbar.pack(side=tk.RIGHT,
                                                    expand=tk.NO,
                                                    fill=tk.Y,
                                                    after=self.rframe_approach_canvas)
                self.approach_mousewheel_setup()
            else:
                self.rframe_approach_canvas.pack_forget()
                self.rframe_approach_scrollbar.pack_forget()
                self.rframe_depart_canvas.pack(side=tk.LEFT,
                                               expand=tk.YES,
                                               fill=tk.BOTH,
                                               after=self.rframe_approach_depart_buttons)
                self.rframe_depart_scrollbar.pack(side=tk.RIGHT,
                                                  expand=tk.NO,
                                                  fill=tk.Y,
                                                  after=self.rframe_depart_canvas)
                self.depart_mousewheel_setup()
            # end if
            self.rframe_approach_depart.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        else:
            self.rframe_approach_depart.pack_forget()
        # end if
    # end rframe_approach_depart_setup

    def lead_blk_setup(self):
        if self.rframe_lead_blk_on is True:
            print("in leadblk setup")
            if self.in_out_selection.get() == 'Lead In Block':
                print("hi")
                self.rframe_lead_out_canvas.pack_forget()
                self.rframe_lead_out_scrollbar.pack_forget()
                self.rframe_lead_in_canvas.pack(side=tk.LEFT,
                                                 expand=tk.YES,
                                                 fill=tk.BOTH,
                                                 after=self.rframe_in_out_buttons)
                self.rframe_lead_in_scrollbar.pack(side=tk.RIGHT,
                                                    expand=tk.NO,
                                                    fill=tk.Y,
                                                    after=self.rframe_lead_in_canvas)
               # self.lead_in_mousewheel_setup()
                self.rframe_in_out.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
            else:
                self.rframe_lead_in_canvas.pack_forget()
                self.rframe_lead_in_scrollbar.pack_forget()
                self.rframe_lead_out_canvas.pack(side=tk.LEFT,
                                               expand=tk.YES,
                                               fill=tk.BOTH,
                                               after=self.rframe_in_out_buttons)
                self.rframe_lead_out_scrollbar.pack(side=tk.RIGHT,
                                                  expand=tk.NO,
                                                  fill=tk.Y,
                                                  after=self.rframe_lead_out_canvas)
                self.lead_out_mousewheel_setup()
            # end if
            self.rframe_in_out.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        else:
            self.rframe_in_out.pack_forget()

    def approach_mousewheel_setup(self):
        self.rframe_approach_canvas.update()
        self.rframe_approach_scrollframe.update()
        if self.rframe_approach_scrollframe.winfo_height() > self.rframe_approach_canvas.winfo_height():
            self.rframe_approach_canvas.bind_all('<MouseWheel>', self.on_approach_mousewheel)
            self.rframe_approach_scrollbar.pack(side=tk.RIGHT, expand=tk.NO, fill=tk.Y,
                                                after=self.rframe_approach_canvas)
        else:
            self.rframe_approach_canvas.unbind_all('<MouseWheel>')
            self.rframe_approach_scrollbar.pack_forget()
        # end if
    # end approach_mousewheel_setup

    def on_approach_mousewheel(self, event):
        self.rframe_approach_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
    # end on_approach_mousewheel

    def depart_mousewheel_setup(self):
        self.rframe_depart_canvas.update()
        self.rframe_depart_scrollframe.update()
        if self.rframe_depart_scrollframe.winfo_height() > self.rframe_depart_canvas.winfo_height():
            self.rframe_depart_canvas.bind_all('<MouseWheel>', self.on_depart_mousewheel)
            self.rframe_depart_scrollbar.pack(side=tk.RIGHT, expand=tk.NO, fill=tk.Y,
                                              after=self.rframe_depart_canvas)
        else:
            self.rframe_depart_canvas.unbind_all('<MouseWheel>')
            self.rframe_depart_scrollbar.pack_forget()
        # end if
    # end approach_mousewheel_setup

    def on_depart_mousewheel(self, event):
        self.rframe_depart_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
    # end on_depart_mousewheel

    def apply_speed_revisions(self, speed_str, start_sentinel, end_sentinel, g_cmds):
        gcode_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
        lines_idxset = gcutils.get_gcode_lines(gcode_lines, start_sentinel, end_sentinel)
        if len(speed_str) > 0 and len(lines_idxset) > 0:
            try:
                speed_mm_per_min = int(speed_str)
                if self.speed_units_option.get() == 'mm/sec':
                    speed_mm_per_min *= 60
                # end if
            except ValueError:
                print('apply_speed_revision: speed value of "{}" invalid'.format(speed_str), file=sys.stderr)
                speed_mm_per_min = None
            # end try/except
            if speed_mm_per_min is not None:
                r_lines_set = gcutils.revise_speed_constant(lines_idxset, speed_mm_per_min, g_cmds, gcode_lines)
                revisions = []
                for i in range(len(r_lines_set)):
                    revisions.append((r_lines_set[i], lines_idxset[i][1], len(r_lines_set[i])))
                # end for i
                self.gcode_scrollable_txt.delete('1.0', tk.END)
                revised_gcode = gcutils.revise_gcode_lines(gcode_lines, revisions)
                for line in revised_gcode:
                    self.gcode_scrollable_txt.insert(tk.END, gcutils.ensure_newline(line))
                # end for line
            # end if
        # end if
    # end apply_speed_revisions

    def apply_epermm_revisions(self, epermm_str, start_sentinel, end_sentinel):
        gcode_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
        lines_idxset = gcutils.get_gcode_lines(gcode_lines, start_sentinel, end_sentinel)
        if len(epermm_str) > 0 and len(lines_idxset) > 0:
            lines_set = [lines for lines, idx in lines_idxset]
            r_lines_set = Epermm.revise_gc_epermm(lines_set, epermm_str, self.extrusion_mode)
            revisions = []
            for i in range(len(r_lines_set)):
                revisions.append((r_lines_set[i], lines_idxset[i][1], len(r_lines_set[i])))
            # end for i
            self.gcode_scrollable_txt.delete('1.0', tk.END)
            revised_gcode = gcutils.revise_gcode_lines(gcode_lines, revisions)
            for line in revised_gcode:
                self.gcode_scrollable_txt.insert(tk.END, gcutils.ensure_newline(line))
            # end for line
        # end if
    # end apply_epermm_revisions

    def approach_depart_apply(self):
        if self.approach_depart_selection.get() == 'Approach a Stop':
            # Coast Section -------------------------------------------------------------
            speed_str = self.approach_coast_speed_entry.get()
            start_sentinel = self.approach_coast_start_sentinel_entry.get()
            end_sentinel = self.approach_coast_end_sentinel_entry.get()
            g_cmds = []
            if self.approach_coast_speed_g0_enable.get() == tk.TRUE:
                g_cmds.append('G0')
            # end if
            if self.approach_coast_speed_g1_enable.get() == tk.TRUE:
                g_cmds.append('G1')
            # end if
            self.apply_speed_revisions(speed_str, start_sentinel, end_sentinel, g_cmds)
            epermm_str = self.approach_coast_e_value_entry.get()
            self.apply_epermm_revisions(epermm_str, start_sentinel, end_sentinel)
            # Join Section -------------------------------------------------------------
            speed_str = self.approach_join_speed_entry.get()
            start_sentinel = self.approach_join_start_sentinel_entry.get()
            end_sentinel = self.approach_join_end_sentinel_entry.get()
            g_cmds = []
            if self.approach_join_speed_g0_enable.get() == tk.TRUE:
                g_cmds.append('G0')
            # end if
            if self.approach_join_speed_g1_enable.get() == tk.TRUE:
                g_cmds.append('G1')
            # end if
            self.apply_speed_revisions(speed_str, start_sentinel, end_sentinel, g_cmds)
            epermm_str = self.approach_join_e_value_entry.get()
            self.apply_epermm_revisions(epermm_str, start_sentinel, end_sentinel)
            # Leadout Section -------------------------------------------------------------
            speed_str = self.approach_leadout_speed_entry.get()
            start_sentinel = self.approach_leadout_start_sentinel_entry.get()
            end_sentinel = self.approach_leadout_end_sentinel_entry.get()
            g_cmds = []
            if self.approach_leadout_speed_g0_enable.get() == tk.TRUE:
                g_cmds.append('G0')
            # end if
            if self.approach_leadout_speed_g1_enable.get() == tk.TRUE:
                g_cmds.append('G1')
            # end if
            self.apply_speed_revisions(speed_str, start_sentinel, end_sentinel, g_cmds)
            epermm_str = self.approach_leadout_e_value_entry.get()
            self.apply_epermm_revisions(epermm_str, start_sentinel, end_sentinel)
        else:
            # Initial Section -------------------------------------------------------------
            speed_str = self.depart_initial_speed_entry.get()
            start_sentinel = self.depart_initial_start_sentinel_entry.get()
            end_sentinel = self.depart_initial_end_sentinel_entry.get()
            g_cmds = []
            if self.depart_initial_speed_g0_enable.get() == tk.TRUE:
                g_cmds.append('G0')
            # end if
            if self.depart_initial_speed_g1_enable.get() == tk.TRUE:
                g_cmds.append('G1')
            # end if
            self.apply_speed_revisions(speed_str, start_sentinel, end_sentinel, g_cmds)
            epermm_str = self.depart_initial_e_value_entry.get()
            self.apply_epermm_revisions(epermm_str, start_sentinel, end_sentinel)
            # Secondary Section -------------------------------------------------------------
            speed_str = self.depart_secondary_speed_entry.get()
            start_sentinel = self.depart_secondary_start_sentinel_entry.get()
            end_sentinel = self.depart_secondary_end_sentinel_entry.get()
            g_cmds = []
            if self.depart_secondary_speed_g0_enable.get() == tk.TRUE:
                g_cmds.append('G0')
            # end if
            if self.depart_secondary_speed_g1_enable.get() == tk.TRUE:
                g_cmds.append('G1')
            # end if
            self.apply_speed_revisions(speed_str, start_sentinel, end_sentinel, g_cmds)
            epermm_str = self.depart_secondary_e_value_entry.get()
            self.apply_epermm_revisions(epermm_str, start_sentinel, end_sentinel)
            # Standard Section -------------------------------------------------------------
            speed_str = self.depart_standard_speed_entry.get()
            start_sentinel = self.depart_standard_start_sentinel_entry.get()
            end_sentinel = self.depart_standard_end_sentinel_entry.get()
            g_cmds = []
            if self.depart_standard_speed_g0_enable.get() == tk.TRUE:
                g_cmds.append('G0')
            # end if
            if self.depart_standard_speed_g1_enable.get() == tk.TRUE:
                g_cmds.append('G1')
            # end if
            self.apply_speed_revisions(speed_str, start_sentinel, end_sentinel, g_cmds)
            epermm_str = self.depart_standard_e_value_entry.get()
            self.apply_epermm_revisions(epermm_str, start_sentinel, end_sentinel)
        # end if
        self.compute_gcode_stats()
    # end approach_apply
    def lead_blk_apply(self):
        lead_in_shape = self.lead_in_shape_selection.get()
        lead_out_shape = self.lead_out_shape_selection.get()
        lead_in_block = None
        lead_out_block = None
        print(self.add_lead_in.get())
        if self.add_lead_in.get():
            lead_in_block = LeadBlock.LeadInOutBlock()
            lead_in_block.set_shape(lead_in_shape)
        if self.add_lead_out.get():
            lead_out_block = LeadBlock.LeadInOutBlock()
            lead_out_block.set_shape(lead_out_shape)

        gc_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
        layer_statistics = LeadBlock.find_layer_beginning_and_end(gc_lines)
        revised_gcode = LeadBlock.clean_gcode(gc_lines)
        revised_gcode = LeadBlock.insert_lead_in_lead_out_blocks(revised_gcode, layer_statistics, lead_in_block, lead_out_block)
        print("In lead block apply")
        #print(revised_gcode)
        self.gcode_scrollable_txt.delete('1.0', tk.END)
        for line in revised_gcode:
            self.gcode_scrollable_txt.insert(tk.END, gcutils.ensure_newline(line))

        pass
    def gframe_setup(self):
        self.gframe0.grid_forget()
        self.gframe1.grid_forget()
        self.gframe2.grid_forget()
        self.gframe3.grid_forget()
        gf_w = self.gframe.winfo_width()
        gf_h = self.gframe.winfo_height()
        if self.gframe_layout == '<Single>':
            self.gframe0.configure(width=gf_w, height=gf_h)
            self.gframe0.grid(row=0, column=0)
        elif self.gframe_layout == '<DoubleVertical>':
            self.gframe0.configure(width=(gf_w - (gf_w / 2)), height=gf_h)
            self.gframe0.grid(row=0, column=0)
            self.gframe1.configure(width=(gf_w / 2), height=gf_h)
            self.gframe1.grid(row=0, column=1)
        elif self.gframe_layout == '<DoubleHorizontal>':
            self.gframe0.configure(width=gf_w, height=(gf_h - (gf_h / 2)))
            self.gframe0.grid(row=0, column=0)
            self.gframe1.configure(width=gf_w, height=(gf_h / 2))
            self.gframe1.grid(row=1, column=0)
        elif self.gframe_layout == '<Quad>':
            self.gframe0.configure(width=(gf_w - (gf_w / 2)), height=(gf_h - (gf_h / 2)))
            self.gframe0.grid(row=0, column=0)
            self.gframe1.configure(width=(gf_w - (gf_w / 2)), height=(gf_h - (gf_h / 2)))
            self.gframe1.grid(row=0, column=1)
            self.gframe2.configure(width=(gf_w / 2), height=(gf_h / 2))
            self.gframe2.grid(row=1, column=0)
            self.gframe3.configure(width=(gf_w / 2), height=(gf_h / 2))
            self.gframe3.grid(row=1, column=1)
        # end if
        self.gframe0.update()
        self.gframe1.update()
        self.gframe2.update()
        self.gframe3.update()
        self.gframe.update()
    # end gframe_setup

    def draw_gcanvas(self, line_segments):
        self.gframe2.update()
        self.gcanvas.configure(width=self.gframe2.winfo_width(), height=self.gframe2.winfo_height())
        current_drawings = self.gcanvas.find_all()
        for drawing in current_drawings:
            self.gcanvas.delete(drawing)
        # end for drawing
        self.gcanvas.create_line(0, 0, 50, 50, 60, 30, fill='White')
        self.gcanvas.place(x=0, y=0)
    # end draw_gcanvas

    def on_resize(self, event):
        self.gframe_setup()
        if self.gcode_open_filename is not None:
            self.display_gcode_txt()
        # end if
        self.rframe.update()
        if self.rframe_approach_depart_on is True:
            if self.approach_depart_selection.get() == 'Approach a Stop':
                self.rframe_approach_canvas.configure(width=140, height=self.rframe.winfo_height())
                self.approach_mousewheel_setup()
            else:
                self.rframe_depart_canvas.configure(width=140, height=self.rframe.winfo_height())
                self.depart_mousewheel_setup()
            # end if
        # end if
    # end on_resize

    @staticmethod
    def exit_program():
        exit()

    # end exit_program

    def display_gcode_txt(self):
        f_w = self.gframe0.winfo_width()
        f_h = self.gframe0.winfo_height()
        px_per_char_w = 8.5
        px_per_char_h = 16.0
        txt_w = math.floor(f_w / px_per_char_w)
        txt_h = math.floor(f_h / px_per_char_h)
        self.gcode_scrollable_txt.configure(width=txt_w, height=txt_h)
        self.gcode_scrollable_txt.frame.update()
        self.gcode_scrollable_txt.update()
        self.gframe0.update()
        f_w = self.gframe0.winfo_width()
        f_h = self.gframe0.winfo_height()
        gf_w = self.gcode_scrollable_txt.frame.winfo_reqwidth()
        gf_h = self.gcode_scrollable_txt.frame.winfo_reqheight()
        gf_we = max(f_w - gf_w, 0)
        gf_he = max(f_h - gf_h, 0)
        self.gcode_scrollable_txt.place(x=math.floor(gf_we / 2), y=math.floor(gf_he / 2))
    # end display_gcode_txt

    def compute_gcode_stats(self):
        if self.gcode_open_filename is not None:
            gcode_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
            o = io.StringIO()
            with redirect_stdout(o):
                GCodeStats.comment_counter(gcode_lines)
                GCodeStats.startstop_counter(gcode_lines, '')
                GCodeStats.sharpangle_counter(gcode_lines, '', 90)
            # end with
            self.gcode_stats.configure(text=o.getvalue())
            self.gcode_stats.update()
            self.gcode_stats.place(x=2, y=2)
        # end if
    # end compute_gcode_stats

    def import_gcode(self):
        filename = tkfd.askopenfilename(initialdir=".",
                                        title="Select a File",
                                        filetypes=[("G-Code Files", "*.g"),
                                                   ("G-Code Files", "*.gcode"),
                                                   ("All Files", "*.*")])
        try:
            f = open(filename, 'r')
        except FileNotFoundError:
            # TODO put message box here
            return
        # end try/except
        self.g_filename.set(filename)
        self.gcode_open_filename = filename
        self.gcode_scrollable_txt.delete('1.0', tk.END)
        gcode_lines = []
        for line in f:
            self.gcode_scrollable_txt.insert(tk.END, line)
            gcode_lines.append(line)
        # end for lines
        f.close()
        self.g_file_label.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X, padx=2, pady=2)
        self.update_extrusion_mode()
        self.display_gcode_txt()
        self.compute_gcode_stats()
        g_limits = gcutils.get_gc_limits(gcode_lines)
        self.g_limits_text.set('X:[{} to {}] | Y:[{} to {}]'.format(
            str(g_limits[0][0]), str(g_limits[0][1]),
            str(g_limits[1][0]), str(g_limits[1][1]))
        )
        self.g_limits_label.pack(after=self.g_extrusion_convert_button,
                                 side=tk.LEFT,
                                 expand=tk.NO, fill=tk.X,
                                 padx=2, pady=2)
    # end import_gcode

    def export_gcode(self):
        filename = tkfd.asksaveasfilename(initialdir=".",
                                          title="Save As",
                                          defaultextension=".gcode",
                                          filetypes=[("G-Code Files", "*.gcode")])
        try:
            f = open(filename, 'w')
        except FileNotFoundError:
            # TODO put message box here
            return
        except FileExistsError:
            # TODO ask to overwrite
            return
        # end try/except
        write_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
        if len(write_lines) > 0 and write_lines[0].find(';Produced by ChromaWare') == 0:
            write_lines[0] = ';Produced by ChromaWare {}'.format(get_software_build_str(5))
        else:
            write_lines.insert(0, ';Produced by ChromaWare {}'.format(get_software_build_str(5)))
        # end if
        f.write('\n'.join(write_lines))
        f.close()
    # end export_gcode

    def close_gcode(self):
        self.gcode_open_filename = None
    # end close_gcode

    def approach_depart_select_toggle(self, value):
        self.rframe_approach_depart_setup()
    # end approach_depart_select_toggle

    def in_out_select_toggle(self, value):
        self.lead_blk_setup()
    def update_extrusion_mode(self):
        if self.gcode_open_filename is not None:
            gcode_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
            self.extrusion_mode = gcutils.detect_extrusion_mode(source_lines=gcode_lines,
                                                                try_to_guess=True,
                                                                max_guess_discrepencies=0)
            extrusion_mode_str = str(self.extrusion_mode)
            self.g_extrusion.set('Extrusion Mode: {}'.format(str(self.extrusion_mode)))
            self.g_extrusion_label.pack(after=self.g_file_label, side=tk.LEFT, expand=tk.NO, fill=tk.X,
                                        ipadx=2, ipady=2, padx=2, pady=2)
            if extrusion_mode_str == 'RELATIVE' or extrusion_mode_str == 'ABSOLUTE':
                complement_str = 'RELATIVE' if extrusion_mode_str == 'ABSOLUTE' else 'ABSOLUTE'
                self.g_extrusion_convert_button_text.set('Convert to {}'.format(complement_str))
                self.g_extrusion_convert_button.pack(after=self.g_extrusion_label, side=tk.LEFT, padx=2)
            # end if
            self.e_per_mm_field_label.place(x=250, y=2)
            self.e_per_mm_field_entry.place(x=250, y=42)
            self.e_per_mm_button.place(x=250, y=82)
        # end if
    # end update_extrusion_mode

    def g_extrusion_convert_button_press(self):
        if self.gcode_open_filename is not None:
            gcode_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
            self.gcode_scrollable_txt.delete('1.0', tk.END)
            desired_extrusion_mode = gcutils.ExtrusionMode.RELATIVE
            if self.extrusion_mode == gcutils.ExtrusionMode.RELATIVE:
                desired_extrusion_mode = gcutils.ExtrusionMode.ABSOLUTE
            # end if
            revised_gcode = gcutils.convert_extrusion_mode(gcode_lines, desired_extrusion_mode)
            for line in revised_gcode:
                self.gcode_scrollable_txt.insert(tk.END, gcutils.ensure_newline(line))
            # end for line
            self.update_extrusion_mode()
            self.compute_gcode_stats()
        # end if
    # end g_extrusion_convert_button_press

    def epermm_button_press(self):
        if self.gcode_open_filename is not None:
            try:
                epermm = float(self.e_per_mm_field_entry.get())
            except ValueError:
                print('Error: Could not determine desired E/mm. Specified Value = "{}"'.format(
                    self.e_per_mm_field_entry.get()
                ), file=sys.stderr)
                return
            # end try/except
            gcode_lines = self.gcode_scrollable_txt.get('1.0', tk.END).split('\n')
            self.gcode_scrollable_txt.delete('1.0', tk.END)
            is_currently_absolute_extrusion = True if self.extrusion_mode == gcutils.ExtrusionMode.ABSOLUTE else False
            revised_gcode = Epermm.revise_gcode_epermm(gcode_lines, epermm,
                                                       absolute_extrusion=is_currently_absolute_extrusion)
            for line in revised_gcode:
                self.gcode_scrollable_txt.insert(tk.END, line)
            # end for line
            self.compute_gcode_stats()
        # end if
    # end epermm_button_press

    def speed_unit_toggle(self, value):
        self.approach_coast_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.approach_join_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.approach_leadout_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))

        self.depart_initial_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.depart_secondary_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))
        self.depart_standard_speed_entry_text.set('Speed ({}):'.format(self.speed_units_option.get()))

    # end speed_unit_toggle

    def lead_blk_button_press(self, event):
        self.lead_blk_label.configure(image=self.lead_blk_img_render_down)
    # end lead_blk_button_press

    def lead_blk_button_release(self, event):
        self.lead_blk_label.configure(image=self.lead_blk_img_render)
        if self.lead_blk_button_armed is True:
            self.rframe_lead_blk_on = not self.rframe_lead_blk_on
            self.rframe_approach_depart_on = False
            self.rframe_approach_depart_setup()
            self.lead_blk_setup()
            pass
        else:
            pass
        # end if
    # end lead_blk_button_release

    def lead_blk_button_enter(self, event):
        self.lead_blk_button_armed = True
        self.lead_blk_label.configure(image=self.lead_blk_img_render_over)
    # end lead_blk_button_enter

    def lead_blk_button_leave(self, event):
        self.lead_blk_button_armed = False
        self.lead_blk_label.configure(image=self.lead_blk_img_render)
    # end lead_blk_button_leave

    def shape_gen_button_press(self, event):
        self.shape_gen_label.configure(image=self.shape_gen_img_render_down)
    # end shape_gen_button_press

    def shape_gen_button_release(self, event):
        self.shape_gen_label.configure(image=self.shape_gen_img_render)
        if self.shape_gen_button_armed is True:
            pass
        else:
            pass
        # end if
    # end lead_blk_button_release

    def shape_gen_button_enter(self, event):
        self.shape_gen_button_armed = True
        self.shape_gen_label.configure(image=self.shape_gen_img_render_over)
    # end shape_gen_button_enter

    def shape_gen_button_leave(self, event):
        self.shape_gen_button_armed = False
        self.shape_gen_label.configure(image=self.shape_gen_img_render)
    # end shape_gen_button_leave

    def infill_button_press(self, event):
        self.infill_btn_label.configure(image=self.infill_btn_img_render_down)
    # end infill_button_press

    def infill_button_release(self, event):
        self.infill_btn_label.configure(image=self.infill_btn_img_render)
        if self.infill_button_armed is True:
            pass
        else:
            pass
        # end if
    # end infill_button_release

    def infill_button_enter(self, event):
        self.infill_button_armed = True
        self.infill_btn_label.configure(image=self.infill_btn_img_render_over)
    # end infill_button_enter

    def infill_button_leave(self, event):
        self.infill_button_armed = False
        self.infill_btn_label.configure(image=self.infill_btn_img_render)
    # end infill_button_leave

    def tipwipe_button_press(self, event):
        self.tipwipe_label.configure(image=self.tipwipe_img_render_down)
    # end tipwipe_button_button_press

    def tipwipe_button_release(self, event):
        self.tipwipe_label.configure(image=self.tipwipe_img_render)
        if self.tipwipe_button_armed is True:
            pass
        else:
            pass
        # end if
    # end tipwipe_button_button_release

    def tipwipe_button_enter(self, event):
        self.tipwipe_button_armed = True
        self.tipwipe_label.configure(image=self.tipwipe_img_render_over)
    # end tipwipe_button_enter

    def tipwipe_button_leave(self, event):
        self.tipwipe_button_armed = False
        self.tipwipe_label.configure(image=self.tipwipe_img_render)
    # end tipwipe_button_leave

    def approach_button_press(self, event):
        self.approach_label.configure(image=self.approach_img_render_down)
    # end approach_button_button_press

    def approach_button_release(self, event):
        self.approach_label.configure(image=self.approach_img_render)
        if self.approach_button_armed is True:
            self.rframe_approach_depart_on = not self.rframe_approach_depart_on
            self.rframe_approach_depart_setup()
        # end if
    # end approach_button_button_release

    def approach_button_enter(self, event):
        self.approach_button_armed = True
        self.approach_label.configure(image=self.approach_img_render_over)
    # end approach_button_enter

    def approach_button_leave(self, event):
        self.approach_button_armed = False
        self.approach_label.configure(image=self.approach_img_render)
    # end approach_button_leave

# end Window


def get_software_build_str(n_nybbles=64):
    hash_nybbles = n_nybbles if 64 >= n_nybbles >= 0 else 64
    version_str = '0.1'  # This is the master version string, update accordingly
    signature_str = ''
    if hash_nybbles > 0:
        signature_str = '-{}'.format(get_software_signature()[0:hash_nybbles])
    # end if
    return 'Build {}{}'.format(version_str, signature_str)
# end get_software_build_str


def get_software_signature():
    file_names = [
        'ChromaWareMain.py',
        'gcutils.py',
        'Epermm.py',
        'GCodeStats.py',
        'LeadBlock.py',
        'LeadBlockBounding.py',
        'LeadBlockClass.py',
    ]
    file_data = bytes([])
    for file_name in file_names:
        with open(file_name, mode='rb') as file:
            file_data += file.read()
            file.close()
        # end with
    # end for file_name
    return sha256(file_data).hexdigest().upper()
# end get_software_signature


def main(argv):
    rootgui = tk.Tk()
    rootgui.wm_title("ChromaWare - {}".format(get_software_build_str(5)))
    rootgui.iconbitmap("img/c3dm32x32.ico")
    initial_width = int(rootgui.winfo_screenwidth() / 2)
    initial_height = int(rootgui.winfo_screenheight() / 2)
    initial_x = int(rootgui.winfo_screenwidth() / 2 - (initial_width / 2))
    initial_y = int(rootgui.winfo_screenheight() / 2 - (initial_height / 2))
    rootgui.geometry('{}x{}+{}+{}'.format(initial_width, initial_height, initial_x, initial_y))
    rootgui.update()
    rootgui.minsize(rootgui.winfo_width(), rootgui.winfo_height())
    GuiWindow(rootgui)
    rootgui.mainloop()
# end main


if __name__ == "__main__":
    main(sys.argv)
# end if