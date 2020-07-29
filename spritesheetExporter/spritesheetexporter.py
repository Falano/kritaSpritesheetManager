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
        self.defaultPath = Path.home().joinpath("spritesheetExportKritaTmp")
        # remember this is a Path, not a string, and as such
        # you can't do string operations on it (unless you convert it first):
        self.exportDir = Path.home()
        # this is a Path too. Trust me.
        self.spritesExportDir = self.defaultPath
        self.isDirectionHorizontal = True
        self.defaultTime = -1
        self.defaultSpace = 0
        self.rows = self.defaultSpace
        self.columns = self.defaultSpace
        self.start = self.defaultTime
        self.end = self.defaultTime
        self.forceNew = False
        self.removeTmp = True
        self.step = 1
        self.layersAsAnimation = False
        self.layersList = []
        self.layersStates = []
        self.offLayers = 0

    def positionLayer(self, layer, imgNum, width, height):
        if self.isDirectionHorizontal:
            layer.move((imgNum % self.columns) * width,
                       (int(imgNum/self.columns)) * height)
        else:
            layer.move(int(imgNum / self.rows) * width,
                       (imgNum % self.rows) * height)

    def checkLayerEnd(self, layer, doc):
        if layer.visible():
            if layer.animated():
                frame = doc.fullClipRangeEndTime()
                while not (layer.hasKeyframeAtTime(frame)
                    or frame < 0):
                    frame -=1
                if self.end < frame:
                    self.end = frame
            if len(layer.childNodes()) != 0:
            # if it was a group layer
            # we also check its kids
                for kid in layer.childNodes():
                    self.checkLayerEnd(kid, doc)

    def checkLayerStart(self, layer, doc):
        if layer.visible():
            if layer.animated():
                frame = 0
                while not (layer.hasKeyframeAtTime(frame)
                    or frame > doc.fullClipRangeEndTime()):
                    frame +=1
                if self.start > frame:
                    self.start = frame
            if len(layer.childNodes()) != 0:
                # if it was a group layer
                # we also check its kids
                for kid in layer.childNodes():
                    self.checkLayerStart(kid, doc)

    # get actual animation duration
    def setStartEndFrames(self):
        doc = Krita.instance().activeDocument()
        layers = doc.topLevelNodes()

    # only from version 4.2.x on can we use hasKeyframeAtTime;
    # in earlier versions we just export from 0 to 100 as default
        ver = Application.version ()
        isNewVersion = (int(ver[0]) > 4 or ( int(ver[0]) == 4 and int(ver[2]) >= 2))

        # get the last frame smaller than
        # the clip end time (whose default is 100)
        if self.end == self.defaultTime:
            if(isNewVersion):
                for layer in layers:
                    self.checkLayerEnd(layer, doc)
            else:
                self.end = 100
        # get first frame of all visible layers
        if self.start == self.defaultTime:
            if(isNewVersion):
                self.start = self.end
                for layer in layers:
                    self.checkLayerStart(layer, doc)
            else:
                self.start = 0
                
    # - export all frames of the animation in a temporary folder as png
    # - create a new document of the right dimensions
    #   according to self.rows and self.columns
    # - position each exported frame in the new doc according to its name
    # - export the doc (aka the spritesheet)
    # - remove tmp folder if needed
    def export(self, debugging=False):


        def debugPrint(message, usingTerminal = True):
            if usingTerminal:
                print(message)
            else:
                QMessageBox.information(QWidget(), i18n("Debug info: "),
                i18n(message))

        def sheetExportPath(suffix=""):
            return self.exportDir.joinpath(self.exportName + suffix)

        def spritesExportPath(suffix=""):
            return self.spritesExportDir.joinpath(self.exportName + suffix)

        def fileNum(num):
            return "_" + str(num).zfill(3)

        def exportFrame(num, doc, debugging = False):
            doc.waitForDone()
            imagePath = str(spritesExportPath(fileNum(num) + ".png"))
            doc.exportImage(imagePath, InfoObject())
            if(debugging):
                debugPrint("exporting frame " + str(num) + " at " + imagePath)
            
        def getLayerState(layer, debugging = False):
            if len(layer.childNodes()) != 0:
                # if it was a group layer
                # we also check its kids
                for kid in layer.childNodes():
                    getLayerState(kid, debugging)
                    
            else:
                self.layersStates.append(layer.visible())
                self.layersList.append(layer)
                if(not layer.visible()):
                    self.offLayers += 1
                if(debugging):
                    debugPrint("saving state " + str(layer.visible()) + 
                    " of layer " + str(layer))

        if debugging:
            print("")
            debugPrint("Export spritesheet start.")

        # clearing lists in case the script is used several times 
        # without restarting krita
        self.layersList.clear()
        self.layersStates.clear()
        self.offLayers = 0

        addedFolder = False
        # create a temporary export directory for the individual sprites
        # if the user didn't set any
        if self.spritesExportDir == self.defaultPath:
            self.spritesExportDir = sheetExportPath("_sprites")

        if self.forceNew and self.spritesExportDir.exists():
            exportNum = 0

            parentPath = self.spritesExportDir.parent
            folder = str(self.spritesExportDir.parts[-1])

            def exportCandidate():
                return parentPath.joinpath(folder + str(exportNum))

            # in case the user has a folder with the exact same name
            # as my temporary one
            while exportCandidate().exists():
                exportNum += 1
            self.spritesExportDir = exportCandidate()

        # if forceNew, spritesExportDir's value is taken
        # from the user-set choices in the dialog

        # this will always be called if not forceNew
        # because it will always create a new export folder
        if not (self.spritesExportDir).exists():
            addedFolder = True
            (self.spritesExportDir).mkdir()

        # render animation in the sprites export folder
        doc = Krita.instance().activeDocument()
        doc.setBatchmode(True)  # so it won't show the export dialog window

        if (not self.layersAsAnimation):
            # check self.end and self.start values
            # and if needed input default value
            if(self.end == self.defaultTime or self.start == self.defaultTime):
                self.setStartEndFrames()
            doc.setCurrentTime(self.start)
            if(debugging):
                if (isNewVersion):
                    debugPrint(
                    "animation Length: " +
                    str(doc.animationLength()) +
                    "; full clip start: " +
                    str(doc.fullClipRangeStartTime()) +
                    "; full clip end: " +
                    str(doc.fullClipRangeEndTime()))
                debugPrint("export start: " +
                str(self.start) +
                "; export end: " +
                str(self.end) +
                "; export length: " +
                str(self.end - self.start)
                )
            framesNum = ((self.end + 1) - self.start)/self.step
            frameIDNum = self.start
            # export frames
            while(doc.currentTime() <= self.end):
                exportFrame(frameIDNum, doc, debugging)
                frameIDNum += self.step
                doc.setCurrentTime(frameIDNum)
            # reset
            frameIDNum = self.start

        else:
            frameIDNum = 0
            # save layers state (visible or not)
            layers = doc.topLevelNodes()
            for layer in layers:
                getLayerState(layer, debugging)
            framesNum = len(self.layersList)
            
            # for compatibility between animated frames as frames
            # and layers as frames
            self.start = 0
            self.end = len(self.layersList)
            
            # hide all layers
            for layer in self.layersList:
                layer.setVisible(False)
                
            # export each visible layer
            while(frameIDNum < len(self.layersStates)):
                if (self.layersStates[frameIDNum]):
                    self.layersList[frameIDNum].setVisible(True)
                    # refresh the canvas
                    doc.refreshProjection()
                    exportFrame(frameIDNum, doc, debugging)
                    self.layersList[frameIDNum].setVisible(False)
                    
                frameIDNum += self.step
            
            # restore layers state
            frameIDNum = 0
            while(frameIDNum < len(self.layersStates)):
                self.layersList[frameIDNum].setVisible(self.layersStates[frameIDNum])
                frameIDNum += 1
                if(debugging):
                    debugPrint("restoring layer " + str(frameIDNum))
            frameIDNum = 0

        # getting current document info
        # so we can copy it over to the new document
        width = doc.width()
        height = doc.height()
        col = doc.colorModel()
        depth = doc.colorDepth()
        profile = doc.colorProfile()
        res = doc.resolution()
        # this is very helpful while programming
        # if you're not quite sure what can be done:
        # debugPrint(dir(doc))

        # getting a default value for rows and columns
        if (self.rows == self.defaultSpace) and (self.columns == self.defaultSpace):
            # square fit
            self.columns = ceil(sqrt(framesNum - self.offLayers))
            self.rows = ceil(float(framesNum - self.offLayers)/self.columns)
            # or one row?
            # self.rows = 1
            # self.columns = framesNum
            if (debugging):
                debugPrint("self.rows: " + str(self.rows) +
                      "; self.columns: " + str(self.columns))

        # if only one is specified, guess the other
        elif (self.rows == self.defaultSpace):
            self.rows = ceil(float(framesNum - self.offLayers)/self.columns)

        # Though if I have to guess the number of columns,
        # it may also change the (user-set) number of rows.
        # For example, if you want ten rows from twelve sprites
        # instead of two rows of two and eight of one,
        # you'll have six rows of two
        elif (self.columns == self.defaultSpace):
            self.columns = ceil(float(framesNum - self.offLayers)/self.rows)
            self.rows = ceil(float(framesNum - self.offLayers)/self.columns)

        # creating a new document where we'll put our sprites
        sheet = Krita.instance().createDocument(
            self.columns * width,
            self.rows * height,
            self.exportName,
            col, depth, profile, res)
        if (debugging):
            debugPrint("new doc name: " + sheet.name())
            debugPrint("old doc width: " + str(width))
            debugPrint("num of frames: " + str(framesNum))
            debugPrint("new doc width: " + str(sheet.width()))

        # adding our sprites to the new document
        # and moving them to the right position
        root_node = sheet.rootNode()
        invisibleLayersNum = 0


        while (frameIDNum < self.end):
            doc.waitForDone()
            if(self.layersStates[frameIDNum]):
                img = str(spritesExportPath(fileNum(frameIDNum) + ".png"))
                if(debugging):
                    debugPrint("managing file " + str(frameIDNum) + " at " + img)
                layer = sheet.createFileLayer(img, img, "ImageToSize")
                root_node.addChildNode(layer, None)
                self.positionLayer(
                    layer=layer,
                    imgNum=(((frameIDNum - invisibleLayersNum)- self.start)/self.step),
                    width=width,
                    height=height)
                # refresh canvas so the layers actually do show
                sheet.refreshProjection()
                if self.removeTmp:
                    # removing temporary sprites exports
                    Path(img).unlink()
                if (debugging):
                    debugPrint("adding to spritesheet, image " + str(frameIDNum-self.start) +
                          " name: " + img +
                          " at pos: " + str(layer.position()))
            else:
                invisibleLayersNum += 1
            frameIDNum += self.step

        # export the document to the export location
        sheet.setBatchmode(True)  # so it won't show the export dialog window
        if debugging:
            debugPrint("exporting spritesheet to " + str(sheetExportPath()))

        sheet.exportImage(str(sheetExportPath(".png")), InfoObject())

        # and remove the empty tmp folder when you're done
        if self.removeTmp:
            if addedFolder:
                self.spritesExportDir.rmdir()

        if debugging:
            debugPrint("All done!")
