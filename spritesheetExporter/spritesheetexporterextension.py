"""
spritesheet exporter from animation timeline
(all visible layers)

"""

from krita import (Extension, krita)

from . import uispritesheetexporter
# manages the dialog that lets you
# set user preferences before applying the script


class spritesheetExporterExtension(Extension):

    # Always initialise the superclass.
    # This is necessary to create the underlying C++ object
    def __init__(self, parent):
        super().__init__(parent)

    # this too is necessary, because "Extension.setup() is abstract
    # and must be overridden" and we inherit from Extension
    def setup(self):
        pass

    # menu stuff
    # don't forget to activate the script in krita's preferences
    # or it won't show
    def createActions(self, window):
        exportSs = window.createAction("pykrita_spritesheetExporter",
                                       "Export As Spritesheet",
                                       "tools/scripts")
        # parameter 1 =  the name that Krita uses to identify the action
        # (where is it used though? For key shortcuts?)
        # parameter 2 = this script's menu entry name
        # parameter 3 = location of menu entry

        exportSs.setToolTip("Export animation in timeline as spritesheet")
        # doesn't show tooltip on mouse hover. Why?

        # when you click on the script in the menu it opens the dialog window
        self.ui = uispritesheetexporter.UISpritesheetExporter()
        exportSs.triggered.connect(self.ui.showExportDialog)


# the actual stuff-doing is in the spritesheetexporter.py script

app = Krita.instance()
# windows and menu stuff
Scripter.addExtension(spritesheetExporterExtension(app))
