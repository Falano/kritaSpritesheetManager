"""
UI of the spritesheet manager user choices dialog
drawing at the end of file

"""


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFormLayout, QVBoxLayout, QFrame, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QLabel,
                             QPushButton, QInputDialog, QSpinBox, QDialog, 
                             QLineEdit, QWidget, QCheckBox, QDialogButtonBox)
import krita
import importlib
from pathlib import Path # to have paths works whether it's windows or unix
from . import spritesheetmanager


class UISpritesheetManager(object):


    def __init__(self):
        # here we don't need super().__init__(parent)
        # maybe it's only for who inherits extensions?
        self.app = krita.Krita.instance()
        self.man = spritesheetmanager.SpritesheetManager()

        self.mainDialog = QDialog(self.app.activeWindow().qwindow()) #the main window
        self.mainDialog.setWindowModality(Qt.NonModal) #The window is not modal and does not block input to other windows.

        self.outerLayout = QVBoxLayout(self.mainDialog) # the box holding everything

        # the user should choose the export name of the final spritesheet
        self.exportName = QLineEdit()

        # and the export directory
        self.exportDirTx = QLineEdit()
        self.exportDirButt = QPushButton("Change Export Directory")
        self.exportDirResetButt = QPushButton("Reset to current Directory")
        self.exportDirButt.clicked.connect(self.changeExportDir)
        self.exportDirResetButt.clicked.connect(self.resetExportDir)
        self.exportDir = QHBoxLayout()
        self.defaultRowsColumnsInfo = QLabel("Leave at 0 to get the default value:")

        self.spinBoxes = QHBoxLayout() # a box holding the boxes with rows columns and start end

        self.rowsColumns = QFormLayout()
        self.rows= QSpinBox()
        self.columns= QSpinBox()
        self.rows.minimum = 0
        self.columns.minimum = 0

        self.startEnd = QFormLayout()
        self.startEnd.setAlignment(Qt.AlignRight)
        self.start = QSpinBox()
        self.end = QSpinBox()
        self.step = QSpinBox()
        self.start.minimum = 0
        self.end.minimum = 0
        self.step.minimum = 1
        self.step.setValue(1)
        self.step.setToolTip("export every 'step' frame")

        # to be placed outside of spinBoxes, still in outerLayout
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.checkBoxes = QHBoxLayout()
        self.overwrite = QCheckBox()
        self.overwrite.setChecked(False)
        self.removeTmp = QCheckBox()
        self.removeTmp.setChecked(True)

        self.line2 = QFrame()
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.OkCancelButtonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.OkCancelButtonBox.accepted.connect(self.confirmButton)
        self.OkCancelButtonBox.rejected.connect(self.mainDialog.close)

        self.space = 10

        self.exportPath = Path.home()

        self.initialize_export()



    # QFormLayout doesn't have addLayout, but QVBoxLayout doesn't have addRow
    # so to have a vertical list of widgets with each its description on the left
    # like AddRow does
    # it seems I need to use a QFormLayout inside a QVBoxLayout
    # for each widget
    def addQuickWidgetDescri(self, parent, dico, align = Qt.AlignLeft):
        layout = QFormLayout()
        for descri, widget in dico.items():
            layout.addRow(descri, widget)
        layout.setAlignment(align)
        parent.addLayout(layout)

    def initialize_export(self):

        # putting stuff in boxes
        self.exportName.setText("Spritesheet")
        exportNameDico = {"Export name:": self.exportName}
        self.addQuickWidgetDescri(parent = self.outerLayout, dico = exportNameDico)

        self.outerLayout.addWidget(self.exportDirTx)
        self.exportDir.addWidget(self.exportDirButt)
        self.exportDir.addWidget(self.exportDirResetButt)

        self.outerLayout.addLayout(self.exportDir)

        self.outerLayout.addWidget(self.defaultRowsColumnsInfo)

        self.rowsColumns.addRow("Rows:", self.rows)
        self.rowsColumns.addRow("Columns:", self.columns)
        self.startEnd.addRow("Start:", self.start)
        self.startEnd.addRow("End:", self.end)
        self.startEnd.addRow("Step:", self.step)

        # and boxes in bigger boxes
        self.spinBoxes.addLayout(self.rowsColumns)
        self.spinBoxes.addLayout(self.startEnd)

        self.outerLayout.addLayout(self.spinBoxes)

        self.outerLayout.addSpacing(self.space)
        self.outerLayout.addWidget(self.line)
        self.outerLayout.addSpacing(self.space)

        # I'm not sure whether I want to let people use the overwrite toggle
        # it could lead to accidentally destroying stuff unless I change the code a bit
        # so for now it's commented
        #checkBoxesDico1 = {"overwrite existant? ": self.overwrite}
        checkBoxesDico2 = {"remove individual sprites? ": self.removeTmp}
        #self.addQuickWidgetDescri(parent = self.checkBoxes, dico = checkBoxesDico1)
        self.addQuickWidgetDescri(parent = self.checkBoxes, dico = checkBoxesDico2)
        self.outerLayout.addLayout(self.checkBoxes)

        self.outerLayout.addLayout(self.exportDir)

        self.outerLayout.addWidget(self.line2)
        self.outerLayout.addSpacing(self.space)

        self.outerLayout.addWidget(self.OkCancelButtonBox)


    def showExportDialog(self):
        self.doc = self.app.activeDocument()
        self.resetExportDir()
        self.mainDialog.resize(500, 300)
        self.mainDialog.setWindowTitle(i18n("SpritesheetExporter"))
        self.mainDialog.setSizeGripEnabled(True)
        self.mainDialog.show()
        self.mainDialog.activateWindow()

    def changeExportDir(self):
        self.exportDirDialog = QFileDialog()
        self.exportDirDialog.setWindowTitle(i18n("Choose Export Directory"))
        self.exportDirDialog.setSizeGripEnabled(True)
        self.exportDirDialog.setDirectory(str(self.exportPath))
        # we grab the output path on directory changed
        self.exportPath = self.exportDirDialog.getExistingDirectory()
        if self.exportPath != "":
            self.exportDirTx.setText(str(self.exportPath))

    # go back to the same folder where your .kra is
    def resetExportDir(self):
        if self.doc:
            self.exportPath = Path(self.doc.fileName()).parents[0]
            self.exportDirTx.setText(str(self.exportPath))


    def confirmButton(self):
        self.man.exportName = self.exportName.text().split('.')[0]
        self.man.rows = self.rows.value()
        self.man.columns = self.columns.value()
        self.man.start = self.start.value()
        self.man.end = self.end.value()
        self.man.step = self.step.value()
        self.man.overwrite = self.overwrite.isChecked()
        self.man.removeTmp = self.removeTmp.isChecked()
        self.man.exportDir = Path(self.exportPath)
        self.man.export()

"""

|----------------------------outer layout: VBoxLayout
| export name
| export directory [    ]
| 0 as default info
||-------------------------------spinBoxes: HBoxLayout
|||------------| |---------------------startEnd: QFormLayout
||| rows <>    | | start <>
||| columns <> | | end <>
|||------------| |-----------------------startEnd--
||------------------------------------spinBoxes--
|(space)
| line -----------
|(space)
||-------------------------------------checkboxes: QFormLayout
|| overwrite[/] remove tmp folder [/]
||-----------------------------------------checkboxes--
|(space)
| line -----------
|(space)
| Ok    Cancel
|--------------------------------------------outer layout--

"""
