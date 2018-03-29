;Generated @ Z0.8
;Modifyied by Hyrel Code Converter Scripts (C3DM Format)
;C3DM Start Code
G21	;To Millimeters
G90	;Absolute coordinates
M203 X2000 Y2000 Z200	;G0 Speed
M104 S0 T12	;Extruder Temp
M140 S0	;Bed Temp
M106 S0 T12	;Fan Speed
M721 S1000 E0 P0 T12	;Un-Prime, Speed, Pulse, Pause, Tool
M722 S1000 E0 P0 T12	;Prime, Speed, Pulse, Pause, Tool

M756 S0.8	;Height for FLOW calculations
M221 P0.16 S1.0 W1.2 Z0.8 T12	;P(10) per nL, S multiplier, W width, Z height, T head
;Total Volume / Distance of Print : 0.0 / 0


;Park From
G0 Z5	
G0 X240 Y10	
G0 X10 Y10	

;Stripped @ Z0.8
;G1 Strip Version 1.0

;Park Go To
G0 X10 Y10	;Rapid to
G0 X240 Y10	;Rapid to
G0 X240 Y220	;Rapid to Park

;CD3M End Code	
M203 X2000 Y2000 Z200	;G0 Speed
M721 S0 E0 P0 T12	;Un-Prime, Speed, Pulse, Pause, Tool
M722 S0 E0 P0 T12	;Prime, Speed, Pulse, Pause, Tool
M103	;Stop Extrusion
M104 S0 T12	;Extruder Temp
M140 S0	;Set Bed Temp
M106 S0 T12	;Fan Speed
M18	;Disable Motors
M30	;End of File GCODE
