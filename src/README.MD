# How to edit Chroma

*General Overview:* Chroma depends on two files simply on two files, Chroma.kv and Chroma.py. Both files are linked and has shared variable names. Please be careful when linking variable name from .kv to .py. All GCode modifying scripts can be found in the scripts folder and kivy/garden is an addon needed for the file browser within Kivy.

*Chroma.py:* Will mainly contain all the function definition used by each of the button and frame found in Chroma. 

*Chroma.kv*: Contain all the visual aspect of the U/I. 

*Print_Parameter.param*: Contain all the parameter used by scripts to generate GCode

*ScriptDetail.txt*: Contain word description of each Scripts which can be access in the U/I

*Debug*: Contain all record of GCode run on the software.
