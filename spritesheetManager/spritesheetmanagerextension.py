"""
spritesheet exporter from animation timeline
(all visible layers)
spritesheet importer to animation if I have time
maybe also merge several one-line spritesheets? Or any already-exported images really

"""

import sys # seems to be used in activating the script; check later
from krita import (Extension, krita)
import importlib
from . import uispritesheetmanager # manages the dialog that lets you set user preferences before applying the script
from pathlib import Path #for path operations # who'd have guessed


class spritesheetManagerExtension(Extension):

    # Always initialise the superclass, This is necessary to create the underlying C++ object
    def __init__(self, parent):
        super().__init__(parent)

# this too is necessary, because "Extension.setup() is abstract and must be overridden" and we inherit from Extension
    def setup(self):
        pass
    
    # menu stuff
    # don't forget to activate the script in krita's preferences or it won't show 
    def createActions (self, window):
        # how do I make sub-menus?
        exportSs = window.createAction("pykrita_spritesheetExporter", "Export As Spritesheet", "tools/scripts/spritesheetmanager")
        #importSs = window.createAction("pykrita_spritesheetImporter", "Import A Spritesheet", "tools/scripts/spritesheetmanager")
        #mergeSs = window.createAction("pykrita_spritesheetMerger", "Merge Spritesheets", "tools/scripts/spritesheetmanager")
        # parameter 1 =  the name that Krita uses to identify the action # where is it used though? For key shortcuts?
        # parameter 2 = this script's menu entry name
        # parameter 3 = location of menu entry

        exportSs.setToolTip("Export animation in timeline as spritesheet") # doesn't show tooltip on mouse hover. Why?

        # when you click on the script in the menu it opens the dialog window
        self.ui = uispritesheetmanager.UISpritesheetManager()
        exportSs.triggered.connect(self.ui.showExportDialog) 
        
  
    # actual stuff-doing in the spritesheetmanager.py script 

app = Krita.instance();
# windows and menu stuff
Scripter.addExtension(spritesheetManagerExtension(app))
