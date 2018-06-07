#!/usr/bin/python
# -*- coding: utf-8 -*-
try:
    import Tkinter as tk
    import tkFileDialog
except:
    import tkinter as tk
    from tkinter import filedialog as tkFileDialog
import platform
import sys
import os
from PIL import Image

# Default Configuration
# ---------------------
# Initial Directory
initial_dir = os.path.normpath(r"~")

# Crop coordinates: upper left corner of crop area
crop_from_x = 0
crop_from_y = 0

# Crop coordinates: bottom right corner of crop area
crop_to_x = -1
crop_to_y = -1

# Resize factor, will be applied on dimensions of the cropped image:
resize_factor = 1.0

# Supported input file types:
supported_types = ['jpg', 'png', 'bmp']


# Standard Output Redirector
# --------------------------
class StdoutRedirector(object):
    def __init__(self, text_widget, master):
        self.text_space = text_widget
        self.master = master

    def write(self, string):
        self.text_space.config(state=tk.NORMAL)
        self.text_space.insert('end', string)
        self.text_space.see('end')
        self.text_space.config(state=tk.DISABLED)
        self.master.update_idletasks()

    def flush(self):
        self.text_space.config(state=tk.NORMAL)
        self.text_space.insert('end', "\n")
        self.text_space.config(state=tk.DISABLED)
        self.master.update_idletasks()

# A Button with disable() and enable() functions
# ----------------------------------------------
class TwoStateButton(tk.Button, object):
    def __init__(self, *args, **kwargs):
        super(TwoStateButton, self).__init__(*args, **kwargs)
        self.enabled_color = 'OliveDrab1'
        self.disabled_color = 'indian red'
        self.my_state = tk.DISABLED
        self.disable()

    def enable(self):
        self.config(state=tk.NORMAL, bg=self.enabled_color)
        self.my_state = tk.NORMAL

    def disable(self):
        self.config(state=tk.DISABLED, bg=self.disabled_color)
        self.my_state = tk.DISABLED

# GUI main class
# --------------
class CropPy:
    def __init__(self, master):
        self.master = master
        self.type_var = tk.StringVar()
        self.type_var.set('.png')
        self.resize_var = tk.StringVar()
        self.resize_var.set('0.8')
        self.resize_var.set(resize_factor)
        self.x1_var = tk.StringVar()
        self.y1_var = tk.StringVar()
        self.x2_var = tk.StringVar()
        self.y2_var = tk.StringVar()
        self.x1_var.set(crop_from_x)
        self.y1_var.set(crop_from_y)
        self.x2_var.set(crop_to_x)
        self.y2_var.set(crop_to_y)

        self.DIR = None
        self.FILES = None
        self.IMG_FILES = None
        self.COUNTER = 0

        bt_padx = 1
        bt_pady = 1

        # -----
        self.button_frame = tk.Frame(self.master)
        self.bt_load = tk.Button(self.button_frame, width=10, height=2, text="Open Directory", command=self.open_dir)
        self.bt_process = TwoStateButton(self.button_frame, width=10, height=2, text="Process Images", command=self.process)

        self.bt_load.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady, fill=tk.X, expand=1)
        self.bt_process.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady, fill=tk.X, expand=1)
        self.button_frame.pack(anchor=tk.W, fill=tk.X)

        # -----
        self.format_frame = tk.Frame(self.master)
        self.type_lbl  = tk.Label(self.format_frame, text='Output Format:')
        self.type0_rbt = tk.Radiobutton(self.format_frame, text='PNG', variable=self.type_var, value='.png')
        self.type1_rbt = tk.Radiobutton(self.format_frame, text='JPG', variable=self.type_var, value='.jpg')
        self.type2_rbt = tk.Radiobutton(self.format_frame, text='BMP', variable=self.type_var, value='.bmp')

        self.type_lbl.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady)
        self.type0_rbt.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady)
        self.type1_rbt.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady)
        self.type2_rbt.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady)
        self.format_frame.pack(anchor=tk.W, fill=tk.X)

        # -----
        self.resize_frame = tk.Frame(self.master)
        self.resize_lbl = tk.Label(self.resize_frame, text='Resize Factor:')
        self.resize_entry = tk.Entry(self.resize_frame, textvariable=self.resize_var, width=5)

        self.resize_lbl.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady)
        self.resize_entry.pack(side=tk.LEFT, pady=bt_pady)
        self.resize_frame.pack(anchor=tk.W, fill=tk.X)

        # -----
        self.coordinates_frame = tk.Frame(self.master)
        self.xy_lbl = tk.Label(self.coordinates_frame, text='Crop Coordinates:')
        self.x1 = tk.Entry(self.coordinates_frame, textvariable=self.x1_var, width=5)
        self.y1 = tk.Entry(self.coordinates_frame, textvariable=self.y1_var, width=5)
        self.x2 = tk.Entry(self.coordinates_frame, textvariable=self.x2_var, width=5)
        self.y2 = tk.Entry(self.coordinates_frame, textvariable=self.y2_var, width=5)

        self.xy_lbl.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady)
        self.x1.pack(side=tk.LEFT, pady=bt_pady)
        self.y1.pack(side=tk.LEFT, pady=bt_pady)
        self.x2.pack(side=tk.LEFT, pady=bt_pady)
        self.y2.pack(side=tk.LEFT, pady=bt_pady)
        self.coordinates_frame.pack(anchor=tk.W, fill=tk.X)

        # -----
        self.info_frame = tk.Frame(self.master)
        self.scb = tk.Scrollbar(self.info_frame)
        self.info_txt = tk.Text(master, height=30, width=20, font=("Courier", 7), yscrollcommand=self.scb.set)
        self.info_txt.config(state=tk.DISABLED)
        self.scb.config(command=self.info_txt.yview)

        self.scb.pack(side=tk.RIGHT, fill=tk.Y, padx=bt_pady, pady=bt_padx)
        self.info_txt.pack(side=tk.LEFT, padx=bt_padx, pady=bt_pady, fill=tk.BOTH, expand=1)
        self.info_frame.pack(anchor=tk.W, fill=tk.BOTH, expand=1)

        # -----
        sys.stdout = StdoutRedirector(self.info_txt, self.master)
        sys.stdout.write("Crop coordinates format: (X1, Y1) and (X2, Y2).\n(Top-left and bottom-right corners of crop-area)\n")


    # Open Directory
    # --------------
    def open_dir(self, dir=None):
        if dir is None:
            # Get dir
            if os.path.exists(initial_dir):
                try:
                    dir = tkFileDialog.askdirectory(title="Choose Image Directory", initialdir=initial_dir)
                except:
                    sys.stdout.write("\nDir not found!\n")
                    return
            else:
                try:
                    dir = tkFileDialog.askdirectory(title="Choose Image Directory")
                except:
                    sys.stdout.write("\nDir not found!\n")
                    return

        # Check dir
        files = os.listdir(dir)
        img_files = []
        counter = 0
        for fn in files:
            for file_type in supported_types:
                if ('.' + file_type) in fn:
                    counter += 1
                    img_files.append(fn)

        # Set variables
        if counter > 0:
            sys.stdout.write("\nDir:  %s\n" % dir)
            sys.stdout.write("%d image/s found:\n" % counter)
            for img_file in img_files:
                sys.stdout.write("  - %s\n" % img_file)

            self.bt_process.enable()
            self.DIR = dir
            self.FILES = files
            self.IMG_FILES = img_files
            self.COUNTER = counter
        else:
            sys.stdout.write("\nNo image files in  %s\n" % dir)
            if self.DIR is not None:
                sys.stdout.write("\nDir:  %s\n" % self.DIR)
                sys.stdout.write("%d image/s found:\n" % self.COUNTER)
                for img_file in self.IMG_FILES:
                    sys.stdout.write("  - %s\n" % img_file)

    # Process images
    # --------------
    def process(self):
        self.open_dir(self.DIR)
        file_type = self.type_var.get()
        x1 = int(float(self.x1_var.get()))
        y1 = int(float(self.y1_var.get()))
        x2 = int(float(self.x2_var.get()))
        y2 = int(float(self.y2_var.get()))
        resize = float(self.resize_var.get())

        sys.stdout.write("\nProcessing images...\n")
        for img_file in self.IMG_FILES:
            # Open image
            img = Image.open(os.path.join(self.DIR, img_file))
            sys.stdout.write("  - %s\n" % img_file)
            sys.stdout.write("    %s  %s  %s\n" % (str(img.format), str(img.size), str(img.mode)))

            # Crop
            this_x2 = x1
            this_y2 = y2
            if x2 < 0 or x2 == x1:
                this_x2 = img.size[0]
            if y2 < 0 or y2 == y1:
                this_y2 = img.size[1]

            cropped = img.crop((x1, y1, this_x2, this_y2))
            size = cropped.size

            # Resize
            new_size = (int(size[0] * resize), int(size[1] * resize))
            cropped.thumbnail(new_size, Image.ANTIALIAS)

            # Save
            cropped.save(os.path.join(self.DIR, 'crop_' + os.path.splitext(img_file)[0] + file_type), quality=95)
        sys.stdout.write("Done!\n")


# ===========================================================================================================
if __name__ == '__main__':
    script_location = os.path.dirname(os.path.realpath(sys.argv[0]))  # get location of scripts
    os_type = platform.system()  # get platform type

    window = tk.Tk()             # create root
    window.title("CropPy v1.0")  # set window title

    if os_type == 'Windows':
        try:
            icon = tk.PhotoImage(file=os.path.join(script_location, "img/icon20x20.gif"))  # load window icon
            window.call('wm', 'iconphoto', window._w, icon)
        except:
            pass
        window.resizable(width=tk.TRUE, height=tk.TRUE)
        window.minsize(290, 200)
    else:
        window.resizable(width=tk.TRUE, height=tk.TRUE)
        window.minsize(310, 59)

    cropPy_gui = CropPy(window)  # create GUI
    window.mainloop()            # run mainloop
# ===========================================================================================================
