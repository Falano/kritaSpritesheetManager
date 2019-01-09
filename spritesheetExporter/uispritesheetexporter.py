"""
UI of the spritesheet exporter user choices dialog

"""


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QFrame, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QLabel,
                             QPushButton, QInputDialog, QSpinBox, QDialog,
                             QLineEdit, QWidget, QCheckBox, QDialogButtonBox,
                             QSpacerItem, QSizePolicy)
import krita
from pathlib import Path  # to have paths work whether it's windows or unix
from . import spritesheetexporter


class describedWidget:
    def __init__(self, widget, descri, tooltip=""):
        self.widget = widget
        self.descri = descri
        self.tooltip = tooltip


class UISpritesheetExporter(object):

    def __init__(self):
        # here we don't need super().__init__(parent)
        # maybe it's only for who inherits extensions?
        self.app = krita.Krita.instance()
        self.exp = spritesheetexporter.SpritesheetExporter()

        # the main window
        self.mainDialog = QDialog(self.app.activeWindow().qwindow())

        # the window is not modal and does not block input to other windows
        self.mainDialog.setWindowModality(Qt.NonModal)

        self.mainDialog.setMinimumSize(500, 100)

        # the box holding everything
        self.outerLayout = QVBoxLayout(self.mainDialog)

        self.topLayout = QVBoxLayout()

        # the user should choose the export name of the final spritesheet
        self.exportName = QLineEdit()

        # and the export directory
        self.exportDirTx = QLineEdit()
        self.exportDirButt = QPushButton("Change export directory")
        self.exportDirResetButt = QPushButton("Reset to current directory")
        self.exportDirResetButt.setToolTip(
            "Reset export directory to current .kra document's directory")
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

        self.customSettings = QCheckBox()
        self.customSettings.setChecked(False)
        self.customSettings.stateChanged.connect(self.toggleHideable)

        self.hideableWidget = QFrame()  # QFrames are a type of widget
        self.hideableWidget.setFrameShape(QFrame.Panel)
        self.hideableWidget.setFrameShadow(QFrame.Sunken)
        self.hideableLayout = QVBoxLayout(self.hideableWidget)

        # We want to let the user choose if they want the final spritesheet
        # to be horizontally- or vertically-oriented.
        # There is a nifty thing called QButtonGroup() but
        # it doesn't seem to let you add names between each checkbox somehow?
        self.horDir = QCheckBox()
        self.horDir.setChecked(True)
        self.vertDir = QCheckBox()
        self.vertDir.setChecked(False)
        self.vertDir.stateChanged.connect(self.exclusiveVertToHor)
        self.horDir.stateChanged.connect(self.exclusiveHorToVert)
        self.direction = QHBoxLayout()

        self.spinBoxesWidget = QFrame()
        self.spinBoxesWidget.setFrameShape(QFrame.Panel)
        self.spinBoxesWidget.setFrameShadow(QFrame.Sunken)

        # a box holding the boxes with rows columns and start end
        self.spinBoxes = QHBoxLayout(self.spinBoxesWidget)

        self.rows = QSpinBox()
        self.columns = QSpinBox()
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
        self.OkCancelButtonBox = \
            QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.OkCancelButtonBox.accepted.connect(self.confirmButton)
        self.OkCancelButtonBox.rejected.connect(self.mainDialog.close)

        self.space = 10

        self.spacer = QSpacerItem(self.space, self.space)
        self.spacerBig = QSpacerItem(self.space*2, self.space*2)

        self.exportPath = Path.home()

        self.initialize_export()

    # I would have used QFormLayout's addRow
    # except it doesn't let you add a tooltip to the row's name
    # (adding a tooltip to the whole layout would have been best
    #  but doesn't seem possible)
    def addDescribedWidget(self, parent, listWidgets, align=Qt.AlignLeft):
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
        # and boxes in bigger boxes
        self.exportName.setText(self.exp.exportName)
        self.addDescribedWidget(parent=self.topLayout, listWidgets=[
            describedWidget(
                widget=self.exportName,
                descri="Export name:",
                tooltip="The name of the exported spritesheet file")])
        self.addDescribedWidget(parent=self.topLayout, listWidgets=[
            describedWidget(
                widget=self.exportDirTx,
                descri="Export Directory:",
                tooltip="The directory the spritesheet will be exported to")])

        self.exportDir.addWidget(self.exportDirButt)
        self.exportDir.addWidget(self.exportDirResetButt)
        self.topLayout.addLayout(self.exportDir)

        # self.outerLayout.addItem(self.spacer)
        self.addDescribedWidget(parent=self.topLayout, listWidgets=[
            describedWidget(
                widget=self.customSettings,
                descri="Use Custom export Settings:",
                tooltip="" +
                "Whether to set yourself the number of rows, columns, \n" +
                "first and last frame, etc. (checked) \n" +
                "or use the default values (unchecked) ")])

        self.outerLayout.addLayout(self.topLayout, 0)

        # all this stuff will be hideable
        self.direction.addWidget(QLabel("sprites placement direction: \t"))
        self.addDescribedWidget(parent=self.direction, listWidgets=[
            describedWidget(
                widget=self.horDir,
                descri="Horizontal:",
                tooltip="like so: \n1, 2, 3 \n4, 5, 6 \n7, 8, 9")])

        self.addDescribedWidget(parent=self.direction, listWidgets=[
            describedWidget(
                widget=self.vertDir,
                descri="Vertical:",
                tooltip="like so: \n1, 4, 7 \n2, 5, 8 \n3, 6, 9")])

        self.hideableLayout.addLayout(self.direction)

        self.hideableLayout.addItem(self.spacerBig)

        defaultsHint = QLabel(
            "Leave any parameter at 0 to get a default value:")
        defaultsHint.setToolTip(
            "For example with 16 sprites, " +
            "leaving both rows and columns at 0 \n" +
            "will set their defaults to 4 each \n" +
            "while leaving only columns at 0 and rows at 1 \n" +
            "will set columns default at 16")
        self.hideableLayout.addWidget(defaultsHint)

        self.addDescribedWidget(parent=self.spinBoxes, listWidgets=[
            describedWidget(
                widget=self.rows,
                descri="Rows:",
                tooltip="Number of rows of the spritesheet; \n" +
                "default is trying to square \n" +
                "or is assigned depending on columns number"),
            describedWidget(
                widget=self.columns,
                descri="Columns:",
                tooltip="Number of columns of the spritesheet; \n" +
                "default is trying to square \n" +
                "or is assigned depending on rows number")])

        self.addDescribedWidget(parent=self.spinBoxes, listWidgets=[
            describedWidget(
                widget=self.start,
                descri="Start:",
                tooltip="" +
                "First frame of the animation timeline (included) " +
                "to be added to the spritesheet; \n" +
                "default is the Start parameter of the Animation docker"),
            describedWidget(
                widget=self.end,
                descri="End:",
                tooltip="Last frame of the animation timeline (included) " +
                "to be added to the spritesheet; \n" +
                "default is the End parameter of the Animation docker"),
            describedWidget(
                widget=self.step,
                descri="Step:",
                tooltip="only consider every 'step' frame " +
                "to be added to the spritesheet; \n" +
                "default is 1 (use every frame)")])

        self.hideableLayout.addWidget(self.spinBoxesWidget)

        self.addDescribedWidget(parent=self.checkBoxes, listWidgets=[
            describedWidget(
                descri="Remove individual sprites?",
                widget=self.removeTmp,
                tooltip="Once the spritesheet export is done, \n"
                + "whether to remove the individual exported sprites")])

        self.overwriteLayout = self.addDescribedWidget(
            parent=self.hiddenCheckboxLayout,
            listWidgets=[
                describedWidget(
                    descri="Overwrite existant?",
                    widget=self.overwrite,
                    tooltip="If there is already a folder " +
                    "with the same name as the individual " +
                    "sprites export folder, \n" +
                    "whether to create a new one (unchecked) " +
                    "or write the sprites in the existing folder, \n"
                    + "possibly overwriting other files (checked)")])

        # self.hideableLayout.addWidget(self.line2)
        # self.hideableLayout.addItem(self.spacer)

        self.addDescribedWidget(parent=self.spritesExportDir, listWidgets=[
            describedWidget(
                widget=self.spritesExportDirTx,
                descri="Sprites export directory:",
                tooltip="The directory the individual sprites " +
                "will be exported to")])
        self.spritesExportDir.addWidget(self.spritesExportDirButt)

        # have removeTmp toggle overwrite's and sprites export dir's visibility
        self.checkBoxes.addWidget(self.hiddenCheckbox)
        self.hideableLayout.addLayout(self.checkBoxes)
        self.hideableLayout.addWidget(self.spritesExportDirWidget)
        self.removeTmp.clicked.connect(self.toggleHiddenParams)

        self.outerLayout.addWidget(self.hideableWidget)
        # self.outerLayout.addItem(self.spacer)
        # self.outerLayout.addWidget(self.line)

        # self.hideableWidget.setSizePolicy(QSizePolicy.Minimum,
        #                                   QSizePolicy.Minimum)
        # (doesn't work)

        self.outerLayout.addWidget(self.OkCancelButtonBox)
        self.toggleHiddenParams()
        self.toggleHideable()

    def exclusiveVertToHor(self):
        self.exclusiveCheckBoxUpdate(
            trigger=self.vertDir,
            triggered=self.horDir)

    def exclusiveHorToVert(self):
        self.exclusiveCheckBoxUpdate(
            trigger=self.horDir,
            triggered=self.vertDir)

    def exclusiveCheckBoxUpdate(self, trigger, triggered):
        if triggered.isChecked() == trigger.isChecked():
            triggered.setChecked(not trigger.isChecked())

    def toggleHideable(self):
        # h = self.mainDialog.height()
        # w = self.mainDialog.width()
        if self.customSettings.isChecked():
            self.hideableWidget.show()
            # self.mainDialog.resize(w, 300)
            self.mainDialog.adjustSize()
        else:
            self.hideableWidget.hide()
            # with only one resize it doesn't work
            # self.mainDialog.resize(w, 0)
            # self.mainDialog.resize(w, 100)
            self.mainDialog.adjustSize()

    def toggleHiddenParams(self):
        if self.removeTmp.isChecked():
            self.overwrite.setChecked(False)
            self.spritesExportDirTx.setText("")
        self.hiddenCheckbox.setDisabled(self.removeTmp.isChecked())
        self.spritesExportDirWidget.setDisabled(self.removeTmp.isChecked())

    def showExportDialog(self):
        self.doc = self.app.activeDocument()
        self.resetExportDir()
        self.mainDialog.setWindowTitle(i18n("SpritesheetExporter"))
        self.mainDialog.setSizeGripEnabled(True)
        self.mainDialog.show()
        self.mainDialog.activateWindow()
        self.mainDialog.setDisabled(False)

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
        self.SpritesExportDirDialog.setWindowTitle(
            i18n("Choose Sprites Export Directory"))
        self.SpritesExportDirDialog.setSizeGripEnabled(True)
        self.SpritesExportDirDialog.setDirectory(str(self.exportPath))
        # we grab the output path on directory changed
        self.spritesExportPath = \
            self.SpritesExportDirDialog.getExistingDirectory()
        if self.spritesExportPath != "":
            self.spritesExportDirTx.setText(str(self.spritesExportPath))

    def confirmButton(self):
        self.mainDialog.setDisabled(True)
        # so if you double click it doesn't interrupt
        # the first run of the function with a new one

        self.exp.exportName = self.exportName.text().split('.')[0]
        self.exp.exportDir = Path(self.exportPath)
        self.exp.isDirectionHorizontal = self.horDir.isChecked()
        self.exp.rows = self.rows.value()
        self.exp.columns = self.columns.value()
        self.exp.start = self.start.value()
        self.exp.end = self.end.value()
        self.exp.step = self.step.value()
        self.exp.removeTmp = self.removeTmp.isChecked()
        self.exp.overwrite = self.overwrite.isChecked()
        if self.spritesExportDirTx.text() != "":
            self.exp.spritesExportDir = Path(self.spritesExportDirTx.text())
        else:
            self.exp.spritesExportDir = ""
            # important: to reset spritesheetexporter's spritesExportDir
        self.exp.export()
        self.mainDialog.hide()
