from krita import (krita, InfoObject)
from math import sqrt, ceil, floor

from . import uispritesheetexporter
# manages the dialog that lets you set user preferences
# before applying the script

from pathlib import Path
# for path operations (who'd have guessed)

from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
# for debug messages


class SpritesheetExporter(object):

    def __init__(self):
        # user-defined variables
        self.exportName = "Spritesheet"
        # remember this is a Path, not a string, and as such
        # you can't do string operations on it (unless you convert it first):
        self.exportDir = Path.home()
        # this is a Path too. Trust me.
        self.spritesExportDir = ""
        self.isDirectionHorizontal = True
        self.rows = 0
        self.columns = 0
        self.start = 0
        self.end = 0
        self.overwrite = False
        self.removeTmp = True
        self.step = 1

    def positionLayer(self, layer, imgNum, width, height):
        if self.isDirectionHorizontal:
            layer.move((imgNum % self.columns) * width,
                       (int(imgNum/self.columns)) * height)
        else:
            layer.move(int(imgNum / self.rows) * width,
                       (imgNum % self.rows) * height)

    # get actual animation duration
    def setStartEndFrames(self):
        doc = Krita.instance().activeDocument()
        layers = doc.topLevelNodes()
        # get first frame of all visible layers
        if self.start == 0:
            for layer in layers:
                if layer.visible() and layer.animated():
                    frame = 0
                    while not (layer.hasKeyframeAtTime(frame)
                        or frame > doc.fullClipRangeEndTime()):
                        frame +=1
                    if self.start > frame:
                        self.start = frame
        # get the last frame smaller than
        # the clip end time (whose default is 100)
        if self.end == 0:
            for layer in layers:
                if layer.visible() and layer.animated():
                    frame = doc.fullClipRangeEndTime()
                    while not (layer.hasKeyframeAtTime(frame)
                        or frame < 0):
                        frame -=1
                    if self.end < frame:
                        self.end = frame


    # - export all frames of the animation in a temporary folder as png
    # - create a new document of the right dimensions
    #   according to self.rows and self.columns
    # - position each exported frame in the new doc according to its name
    # - export the doc (aka the spritesheet)
    # - remove tmp folder if needed
    def export(self, debugging=False):

        addedFolder = False
        # create a temporary export directory for the individual sprites
        # if the user didn't set any
        if self.spritesExportDir == "":
            self.spritesExportDir = \
                self.exportDir.joinpath(self.exportName + "_sprites")

        if not self.overwrite and self.spritesExportDir.exists():
            exportNum = 0

            parentPath = self.spritesExportDir.parent
            folder = str(self.spritesExportDir.parts[-1])

            # in case the user has a folder with the exact same name
            # as my temporary one
            while (parentPath.joinpath(folder + str(exportNum)).exists()):
                exportNum += 1

            self.spritesExportDir = \
                parentPath.joinpath(folder + str(exportNum))

        # if overwrite, spritesExportDir's value is taken
        # from the user-set choices in the dialog

        # this will always be called if not overwrite
        # because it will always create a new export folder
        if not (self.spritesExportDir).exists():
            addedFolder = True
            (self.spritesExportDir).mkdir()

        # render animation in the sprites export folder
        doc = Krita.instance().activeDocument()

        # check self.end and self.start values
        # and if needed input default value
        if(self.end == 0 and self.start == 0):
            self.setStartEndFrames()
        # give default value to step
        if (self.step == 0):
            self.step = 1
        doc.setCurrentTime(self.start)
        if(debugging):
            print("animation Length: " +
                  str(doc.animationLength()) +
                  "; full clip self.start: " +
                  str(doc.fullClipRangeStartTime()) +
                  "; full clip self.end: " +
                  str(doc.fullClipRangeEndTime()) +
                  "; playback self.start time: " +
                  doc.playbackStartTime() +
                  "; playback self.end time: " +
                  playbackEndTime())
        framesNum = ((self.end + 1) - self.start)/self.step
        # it would be better to have the default value be
        # from first to last effective frame instead of asking the user
        # to correctly set the Start and End anim values each time,
        # but as of now krita can't I think
        doc.setBatchmode(True)  # so it won't show the export dialog window
        tmpNum = self.start
        while(doc.currentTime() <= self.end):
            imageName = self.exportName + "_" + str(tmpNum).zfill(3) + ".png"
            imagePath = str(self.spritesExportDir.joinpath(imageName))
            doc.exportImage(imagePath, InfoObject())
            doc.setCurrentTime(doc.currentTime() + self.step)
            tmpNum += self.step

        # getting current document info
        # so we can copy it over to the new document
        width = doc.width()
        height = doc.height()
        col = doc.colorModel()
        depth = doc.colorDepth()
        profile = doc.colorProfile()
        res = doc.resolution()
        # print(dir(doc))

        # getting a default value for rows and columns
        if (self.rows == 0) and (self.columns == 0):
            # square fit
            self.columns = ceil(sqrt(framesNum))
            self.rows = ceil(float(framesNum)/self.columns)
            # or one row?
            # self.rows = 1
            # self.columns = framesNum
            if (debugging):
                print("self.rows: " + str(self.rows) +
                      "; self.columns: " + str(self.columns))

        # if only one is specified, guess the other
        elif (self.rows == 0):
            self.rows = ceil(float(framesNum)/self.columns)

        # Though if I have to guess the number of columns,
        # it may also change the (user-set) number of rows.
        # For example, if you want ten rows from twelve sprites
        # instead of two rows of two and eight of one,
        # you'll have six rows of two
        elif (self.columns == 0):
            self.columns = ceil(float(framesNum)/self.rows)
            self.rows = ceil(float(framesNum)/self.columns)

        # creating a new document where we'll put our sprites
        sheet = Krita.instance().createDocument(
            self.columns * width,
            self.rows * height,
            self.exportName,
            col, depth, profile, res)
        if (debugging):
            print("new doc name: " + sheet.name())
            print("old doc width: " + str(width))
            print("num of frames: " + str(framesNum))
            print("new doc width: " + str(sheet.width()))

            # for debugging when the result of print() is not available
            # QMessageBox.information(QWidget(), i18n("Debug 130"),
            #                         i18n("step: " + str(self.step) +
            #                              "; end: " + str(self.end) +
            #                              "; start: " + str(self.start) +
            #                              "; rows: " + str(self.rows) +
            #                              "; columns: " + str(self.columns) +
            #                              "; frames number: " +
            #                              str(framesNum)))

        # adding our sprites to the new document
        # and moving them to the right position
        imgNum = self.start
        root_node = sheet.rootNode()

        while (imgNum <= self.end):
            imageName = self.exportName + "_" + str(imgNum).zfill(3) + ".png"
            img = str(self.spritesExportDir.joinpath(imageName))
            layer = sheet.createFileLayer(img, img, "ImageToSize")
            root_node.addChildNode(layer, None)
            self.positionLayer(
                layer=layer,
                imgNum=((imgNum-self.start)/self.step),
                width=width,
                height=height)
            # I need to merge down each layer or they don't show
            layer.mergeDown()
            if self.removeTmp:
                # removing temporary sprites exports
                Path(img).unlink()
            if (debugging):
                print("image " + str(imgNum-self.start) +
                      " name: " + img +
                      " at pos:")
                print(layer.position())
            imgNum += self.step

        # export the document to the export location
        sheet.setBatchmode(True)  # so it won't show the export dialog window
        if debugging:
            print("exporting spritesheet to " +
                  str(self.exportDir.joinpath(self.exportName)))

        exportImagePath = \
            str(self.exportDir.joinpath(self.exportName)) + ".png"
        sheet.exportImage(exportImagePath, InfoObject())

        # and remove the empty tmp folder when you're done
        if self.removeTmp:
            if addedFolder:
                self.spritesExportDir.rmdir()
