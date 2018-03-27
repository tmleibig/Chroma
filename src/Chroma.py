from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from kivy.uix.textinput import TextInput
from kivy.utils import platform
from kivy.garden.FileBrowser import FileBrowser
from os.path import sep, expanduser, isdir, dirname
from kivy.config import Config
from shutil import copyfile

# Setting size of U/I
Config.set('graphics', 'width', '1100')
Config.set('graphics', 'height', '650')

import sys
import webbrowser
import os
import subprocess
import re
import errno
import datetime

#Defining Window Class

class LoadGC(FloatLayout):
    directory = ObjectProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class LoadParam(FloatLayout):
    directory = ObjectProperty(None)
    load_param = ObjectProperty(None)
    cancel = ObjectProperty(None)

class AddSC(FloatLayout):
    directory = ObjectProperty(None)
    add = ObjectProperty(None)
    cancel = ObjectProperty(None)

class Notification(FloatLayout):
    fname =  StringProperty(None)
    cancel = ObjectProperty(None)
    open = ObjectProperty(None)
    simu = ObjectProperty(None)

class Error(FloatLayout):
    error =  StringProperty(None)
    cancel = ObjectProperty(None)

#Placeholder for list adapter, serve no puposes.
class ScriptButton(ListItemButton):
    def print_pos(self, mybutton):
        print(self.pos)

class ScriptDetail(FloatLayout):
    script = StringProperty(None)
    cancel = ObjectProperty(None)

#Defining everything in Root

class Root(FloatLayout):
    #Contain actual text within GCode
    text_input = ObjectProperty(None)
    #Contain Text Path for GCode Input. Including Path
    file_name = ObjectProperty(None)
    #Contain Text Path for Parameter File. Including Path
    param_name = ObjectProperty(None)
    #Contain the actual text of Param File
    text_param = ""
    #Contain the full path name of final file path (Where original GCode is found)
    dest_path = ""
    #Contain text for rename
    rename = None
    directory = os.getcwd()
    script_list = []


    #Define how the list of scripts will look like
    list_args_convert = lambda row_index, obj: {'text': obj.split("\\")[-1],
                                                'size_hint_y': None,
                                                'height':25}

    #Use to display the list of script in script_list
    list_adapter = ListAdapter(data = script_list,
                               args_converter=list_args_convert,
                               selection_mode='single',
                               propagate_selection_to_data=False,
                               allow_empty_selection=False,
                               cls=ScriptButton)

    # Move selected script up by one
    def moveup(self):
        for item in self.list_adapter.selection:
            item_path = os.path.join(self.directory, item.text)
            position = self.list_adapter.data.index(item_path)
            #print(position)
            if position == 0:
                pass
            else:
                self.list_adapter.data.remove(item_path)
                self.list_adapter.data.insert(position-1, item_path)

    # Move selected script down by one
    def movedown(self):
        for item in self.list_adapter.selection:
            item_path = os.path.join(self.directory, item.text)
            position = self.list_adapter.data.index(item_path)
            #print(position)
            self.list_adapter.data.remove(item_path)
            self.list_adapter.data.insert(position+1, item_path)

    #Only work for file within directory. Remove script from list of scripts
    def remove(self):
        for item in self.list_adapter.selection:
            remove_item = str(self.directory+"\\"+item.text)
            self.list_adapter.data.remove(remove_item)

    #Apply scripts onto file_input
    def convert(self):
        scriptorder = self.list_adapter.data
        file = self.file_name.text
        param = self.param_name
        origin_file = file

        #Splicing file path into path, file_name, and file_type
        fargue = file.split("\\")
        fdat = fargue[-1].split(".")
        path = "\\".join(fargue[:-1])
        file_name = fdat[0]
        file_type = fdat[1]

        #Final destination of output file
        dest = ""

        #Record output of running python scripts. Only currently work when applying the latest script
        result = 0

        #Check if param is initialize and the program has it
        if (param == None):
            output = "No param file detected, please load in param file."
            content = Error(error=output, cancel=self.dismiss_popup)
            self._popup = Popup(title="No Param File", content=content, size_hint=(0.9, None), height=200)
            self._popup.open()
            return

        #Check if the file selected is in the same working directory. If not copy the file into the directory
        if path != self.directory:
            new_file = self.directory+"\\"+file_name+"."+file_type
            copyfile(file, new_file)
            file = new_file
            origin_file = new_file

        #Apply scripts in order with each output being the input for the next script
        for i in scriptorder:
            result = subprocess.run(["python", i, file , str(param)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            fargue = file.split("\\")
            fdat = fargue[-1].split(".")
            filename = fdat[0]
            filetype = fdat[1]
            fargue[-1] = filename+"_fixed."+filetype
            file = "\\".join(fargue)

        #Check for file rename (rename needs to have .GCode in it). If rename exist then create the new file and copy final output into that file. If not
        #generate a new filename appropriate for the final output file
        if self.rename != None:
           dest =  path+"\\"+self.rename
           outfile = open(dest, 'w')
           with open(file) as f:
               for r in f:
                   outfile.write(r)
               file = dest
           self.dest_path = path
        else:
            new_file_name = file_name + "_POSTSCRIPT"
            dest = path+"\\"+new_file_name+"."+file_type
            copyfile(file, dest)
            self.dest_path = path

        out_ft = file.split("\\")[-1].split(".")
        #Check to see if output of file is correct
        if out_ft[-1].lower() != "gcode":
            filetype = test[-1]

            output = "Ending file type is: '" + filetype + "' \nPlease check your filename to have the correct filetype (GCode)"
            content = Error(error=output, cancel=self.dismiss_popup)
            self._popup = Popup(title="Possible failure", content=content, size_hint=(0.9, None), height=200)
            self._popup.open()
        else:
            #Return success or failure depending on error produce by code.
            if result.returncode == 0:
                #Generating and Creating new Directory
                now = datetime.datetime.now()
                time_now = now.strftime("%m-%d %H-%M-%S")
                new_directory = self.directory+"\\debug\\"+file_name+" "+time_now
                print("new directory is:  "+new_directory)
                try:
                    os.makedirs(new_directory)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

                #Generate new path for new file and start copying over all current
                #temp file generated in source folder over into directory generated above
                #Remove all temp file found left
                new_file = new_directory+"\\"+file_name+"."+file_type
                orf = origin_file
                copyfile(origin_file, new_file)
                for i in scriptorder:
                    fargue = origin_file.split("\\")
                    fdat = fargue[-1].split(".")
                    filename = fdat[0]
                    filetype = fdat[1]
                    fargue[-1] = filename+"_fixed."+filetype
                    origin_file = "\\".join(fargue)

                    new_file = new_directory+"\\"+fargue[-1]
                    copyfile(origin_file, new_file)
                    os.remove(origin_file)
                os.remove(orf)

                #Splice out file name for output display
                sfile = dest.split('\\')
                filename = "Output name is:" + str(sfile[-1])
                content = Notification(fname=filename,cancel=self.dismiss_popup, open=self.open, simu=self.opensimu_file)
                self._popup = Popup(title="File has been created", content=content, size_hint=(0.9, None), height=150)
                self._popup.open()
            else:
                err = result.stderr.decode("utf-8")
                content = Error(error=err, cancel=self.dismiss_popup)
                self._popup = Popup(title="Script has failed", content=content, size_hint=(0.9, None), height=400)
                self._popup.open()


    #IN TESTING DO NOT USE
    def opensimu(self):
        #webbrowser.open("https://nraynaud.github.io/webgcode/")
        filename = os.getcwd() +"\\CAMotics\\camotics.exe"
        subprocess.call([filename, self.file_name.text])

    #IN TESTING DO NOT USE
    def opensimu_file(self, file):
        filename = os.getcwd() + "\\CAMotics\\camotics.exe"
        subprocess.call([filename, file])

    #Dismiss pop_up notification made by app
    def dismiss_popup(self):
        self._popup.dismiss()

    #Dismiss file browser
    def dismiss_filebs(self, instance):
        self._popup.dismiss()

    #Use to update the text for text_input
    def update(self, string):
        with open(string) as stream:
            self.text_input.text = stream.read()

    #Select and copy all text within text_input.
    def copy(self):
        Clipboard.copy(self.text_input.text)

    #Function to generate the U/I to add script
    def add_to_list(self):
        content = AddSC(directory = self.directory,add =self.add, cancel=self.dismiss_popup)
        fb_content = FileBrowser(select_string = 'Select',path = self.directory, on_canceled = self.dismiss_filebs, multiselect = True, dirselect = True, on_success = self.add_fb, filters = ['*.py'])
        self._popup = Popup(title="Add file", content=fb_content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def add_fb(self, instance):
        self.add(instance.path, instance.selection)

    #Function to add a script into script_list
    def add(self, path, filename):
        for i in range(0,len(filename)):
            self.list_adapter.data.append(str(os.path.join(path, filename[i])))
            self.directory = os.getcwd()
            self.dismiss_popup()

    #Function to generate U/I to load gcode file
    def show_load(self):
        content = LoadGC(directory = self.directory,load=self.load, cancel=self.dismiss_popup)
        fb_content = FileBrowser(select_string = 'Select',path = self.directory, on_canceled = self.dismiss_filebs, dirselect = True, on_success = self.load_fb, filters = ['*GCode'])
        self._popup = Popup(title="Load file", content=fb_content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    #Function to generate U/I to load in param file
    def show_param_list(self):
        content = LoadParam(directory = self.directory, load_param=self.load_param, cancel=self.dismiss_popup)
        fb_content = FileBrowser(select_string = 'Select',path = self.directory, on_canceled = self.dismiss_filebs, dirselect = True, on_success = self.load_param_fb, filters = ['*.param'])
        self._popup = Popup(title="Load Parameter File", content=fb_content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    #Call on load_param by using new file browser
    def load_param_fb(self, instance):
        self.load_param(instance.path, instance.selection)

    #Call on load by using new file browser
    def load_fb(self, instance):
        self.load(instance.path, instance.selection)

    #Function to add param text into window and store path name
    def load_param(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.text_param.text = stream.read()

        self.param_name = str(os.path.join(path, filename[0]))
        print(self.param_name)
        self.directory = os.getcwd()
        self.dismiss_popup()

    #Function to add file_input text into window and store path name
    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.text_input.text = stream.read()

        self.file_name.text = str(os.path.join(path, filename[0]))
        self.directory = os.getcwd()
        self.dismiss_popup()

    #Function to open file
    def open(self, text):
        direc = self.dest_path
        full_name = os.path.join(direc, text.split(":")[-1])
        os.startfile(full_name, 'open')

    #Function to display detail of a script
    #ScriptDetail.txt musst be found in the same directory to work.
    def opendetail(self):
        if not os.path.isfile("ScriptDetail.txt"):
            content = Error(error="ScriptDetail.txt does not exist", cancel=self.dismiss_popup)
            self._popup = Popup(title="Error", content=content, size_hint=(0.9, None), height=400)
            self._popup.open()

        for item in self.list_adapter.selection:
            print(item.text)
            spit = item.text.split("\\")
            print(spit[-1])
            file = re.compile(spit[-1])
            path = os.getcwd()
            script = str(os.path.join(path, "ScriptDetail.txt"))
            result = "No detail on file can be found."
            with open(script) as f:
                for r in f:
                     if re.search(file,r) is not None:
                         line = r.split(":")
                         result = line[-1]
            param = re.compile("<<[a-zA-Z0-9 ]+>>")
            detail = ""
            for r in result.split():
                if re.search(param, r) is not None:
                   detail += "\n"
                detail += r
                detail += " "
            content = ScriptDetail(script=detail,cancel=self.dismiss_popup)
            self._popup = Popup(title="Detail of Script", content=content, size_hint=(0.9, None), height=300)
            self._popup.open()


    def exit(self):
        exit()

    #Function to set new name for output file
    def validatename(self, text):
        self.rename = text

    #Debug function
    def setname(self):
        print(self.rename)

class Chroma(App):
    pass

Factory.register('Root', cls=Root)
Factory.register('LoadGC', cls=LoadGC)
Factory.register('AddSC', cls=AddSC)
Factory.register('LoadParam', cls=LoadParam)

if __name__ == '__main__':
    sys.stderr = open('errorlog.txt', 'w')
    Chroma().run()
    sys.stderr.close()
    sys.stderr = sys.__stderr__
