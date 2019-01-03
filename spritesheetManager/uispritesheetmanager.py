"""
UI of the spritesheet manager user choices dialog
drawing of the structure of the dialog at the end of file

"""


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QFrame, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QLabel,
                             QPushButton, QInputDialog, QSpinBox, QDialog, 
                             QLineEdit, QWidget, QCheckBox, QDialogButtonBox,
                             QSpacerItem)
import krita
import importlib
from pathlib import Path # to have paths works whether it's windows or unix
from . import spritesheetmanager

        
class describedWidget:
    def __init__ (self, widget, descri, tooltip = ""):
        self.widget = widget
        self.descri = descri
        self.tooltip = tooltip


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
        self.exportDirButt = QPushButton("Change export directory")
        self.exportDirResetButt = QPushButton("Reset to current directory")
        self.exportDirResetButt.setToolTip("Reset export directory to current .kra document's directory")
        self.exportDirButt.clicked.connect(self.changeExportDir)
        self.exportDirResetButt.clicked.connect(self.resetExportDir)
        self.exportDir = QHBoxLayout()
        
        # and the sprites export directory
        self.spritesExportDirWidget = QWidget()
        self.spritesExportDirTx = QLineEdit()
        self.spritesExportDirButt = QPushButton("Change sprites directory")
        self.spritesExportDirButt.clicked.connect(self.changeSpritesExportDir)
        self.spritesExportDirTx.setToolTip("Leave empty for default")
        self.spritesExportDir = QHBoxLayout(self.spritesExportDirWidget)
        
        self.defaultRowsColumnsInfo = QLabel("Leave at 0 to get the default value:")

        self.spinBoxes = QHBoxLayout() # a box holding the boxes with rows columns and start end

        self.rows= QSpinBox()
        self.columns= QSpinBox()
        self.rows.minimum = 0
        self.columns.minimum = 0

        self.start = QSpinBox()
        self.end = QSpinBox()
        self.step = QSpinBox()
        self.start.minimum = 0
        self.end.minimum = 0
        self.step.minimum = 1
        self.step.setValue(1)

        # to be placed outside of spinBoxes, still in outerLayout
        self.hiddenCheckbox = QWidget()
        self.hiddenCheckboxLayout = QVBoxLayout(self.hiddenCheckbox)
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
        
        self.spacer = QSpacerItem(self.space, self.space)
        self.spacerBig = QSpacerItem(self.space*2, self.space*2)

        self.exportPath = Path.home()

        self.initialize_export()



    # I would have used QFormLayout's addRow
    # except it doesn't let you add a tooltip to the row's name
    # (adding a tooltip to the whole layout would have been best but doesn't seem possible)
    def addDescribedWidget(self, parent, listWidgets, align = Qt.AlignLeft):
        layout = QGridLayout()
        row = 0
        for widget in listWidgets:
            label = QLabel(widget.descri)
            label.setBuddy(widget.widget)
            layout.addWidget(label, row, 0)
            layout.addWidget(widget.widget, row, 1)
            if widget.tooltip != "":
                widget.widget.setToolTip(widget.tooltip)
                label.setToolTip(widget.tooltip)
            row += 1
        layout.setAlignment(align)
        parent.addLayout(layout)
        return layout





    def initialize_export(self):

        # putting stuff in boxes
        self.exportName.setText(self.man.exportName)
        self.addDescribedWidget(parent = self.outerLayout, listWidgets = [
        describedWidget(
        widget = self.exportName, 
        descri = "Export name:", 
        tooltip = "The name of the exported spritesheet file")])
        self.addDescribedWidget(parent = self.outerLayout, listWidgets = [
        describedWidget(
        widget = self.exportDirTx, 
        descri = "Export Directory:", 
        tooltip = "The directory the spritesheet will be exported to")])
        
        self.exportDir.addWidget(self.exportDirButt)
        self.exportDir.addWidget(self.exportDirResetButt)
        self.outerLayout.addLayout(self.exportDir)


        self.outerLayout.addItem(self.spacerBig)


        self.outerLayout.addWidget(self.defaultRowsColumnsInfo)

        self.addDescribedWidget(parent = self.spinBoxes, listWidgets = [
        describedWidget(
        widget = self.rows, 
        descri = "Rows:", 
        tooltip = "Number of rows of the spritesheet; \ndefault is trying to square"), 
        describedWidget(
        widget = self.columns, 
        descri = "Columns:", 
        tooltip = "Number of columns of the spritesheet; \ndefault is trying to square")])
        
        self.addDescribedWidget(parent = self.spinBoxes, listWidgets = [
        describedWidget(
        widget = self.start, 
        descri = "Start:", 
        tooltip = "First frame of the animation timeline (included) to be added to the spritesheet; \ndefault is the Start parameter of the Animation docker"), 
        describedWidget(
        widget = self.end, 
        descri = "End:", 
        tooltip = "Last frame of the animation timeline (included) to be added to the spritesheet; \ndefault is the End parameter of the Animation docker"), 
        describedWidget(
        widget = self.step, 
        descri = "Step:", 
        tooltip = "only consider every 'step' frame to be added to the spritesheet; \ndefault is 1 (use every frame)")])


        # and boxes in bigger boxes
        self.outerLayout.addLayout(self.spinBoxes)

        self.addDescribedWidget(parent = self.checkBoxes, listWidgets = [
        describedWidget(
        descri = "Remove individual sprites?", 
        widget = self.removeTmp, 
        tooltip = "Once the spritesheet export is done, \nwhether to remove the individual exported sprites")])
        
        self.overwriteLayout = self.addDescribedWidget(parent = self.hiddenCheckboxLayout, listWidgets = [
        describedWidget(
        descri = "Overwrite existant?", 
        widget = self.overwrite, 
        tooltip = "If there is already a folder with the same name as the individual sprites export folder, \nwhether to create a new one (unchecked) or write the sprites in the existing folder, \npossibly overwriting other files (checked)")])
        
        self.outerLayout.addWidget(self.line2)
        self.outerLayout.addItem(self.spacer)
        
        
        self.addDescribedWidget(parent = self.spritesExportDir, listWidgets = [
        describedWidget(
        widget = self.spritesExportDirTx, 
        descri = "Sprites export directory:", 
        tooltip = "The directory the individual sprites will be exported to")])
        self.spritesExportDir.addWidget(self.spritesExportDirButt)
        
        # have removeTmp toggle overwrite's and sprites export dir's visibility
        self.checkBoxes.addWidget(self.hiddenCheckbox)
        self.outerLayout.addLayout(self.checkBoxes)
        self.outerLayout.addWidget(self.spritesExportDirWidget)
        self.removeTmp.clicked.connect(self.toggleHiddenParams)

        self.outerLayout.addItem(self.spacer)
        self.outerLayout.addWidget(self.line)

        self.outerLayout.addWidget(self.OkCancelButtonBox)
        
        self.toggleHiddenParams()

    def toggleHiddenParams(self):
        if self.removeTmp.isChecked():
            self.overwrite.setChecked(False)
            self.spritesExportDirTx.setText("")
        self.hiddenCheckbox.setDisabled(self.removeTmp.isChecked())
        self.spritesExportDirWidget.setDisabled(self.removeTmp.isChecked())

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

    def changeSpritesExportDir(self):
        self.SpritesExportDirDialog = QFileDialog()
        self.SpritesExportDirDialog.setWindowTitle(i18n("Choose Sprites Export Directory"))
        self.SpritesExportDirDialog.setSizeGripEnabled(True)
        self.SpritesExportDirDialog.setDirectory(str(self.exportPath))
        # we grab the output path on directory changed
        self.spritesExportPath = self.SpritesExportDirDialog.getExistingDirectory()
        if self.spritesExportPath != "":
            self.spritesExportDirTx.setText(str(self.spritesExportPath))

    def confirmButton(self):
        self.man.exportName = self.exportName.text().split('.')[0]
        self.man.exportDir = Path(self.exportPath)
        self.man.rows = self.rows.value()
        self.man.columns = self.columns.value()
        self.man.start = self.start.value()
        self.man.end = self.end.value()
        self.man.step = self.step.value()
        self.man.removeTmp = self.removeTmp.isChecked()
        self.man.overwrite = self.overwrite.isChecked()
        if self.spritesExportDirTx.text() != "":
            self.man.spritesExportDir = Path(self.spritesExportDirTx.text())
        else:
            self.man.spritesExportDir = "" # important to reset spritemanager's spritesExportDir
        self.man.export()

"""

|----------------------------outer layout: VBoxLayout
| export name
| export directory [    ]
|(space)
| 0 as default info
||-------------------------------spinBoxes: HBoxLayout
|||------------| |---------------------unnamed QGridLayout
||| rows <>    | | start <>
||| columns <> | | end <>
|||------------| |-----------------------unnamed QGridLayout--
||------------------------------------spinBoxes--
| line -----------
|(space)
||-------------------------------------checkboxes: QHBoxLayout
|| remove tmp folder[/] overwrite [/]
||-----------------------------------------checkboxes--
|(space)
| line -----------
| Ok    Cancel
|--------------------------------------------outer layout--

"""
