import sys # seems to be used in activating the script; check later
from krita import * #(Extension, krita, InfoObject)
import importlib
from glob import glob # to get files in a directory
from math import sqrt, ceil, floor
from . import uispritesheetmanager # manages the dialog that lets you set user preferences before applying the script
from pathlib import Path #for path operations # who'd have guessed
from shutil import rmtree

from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox # for debug messages


class SpritesheetManager(object):

    def __init__(self):
        # user-defined variables
        # currently, placeholders    
        # exporter
        self.exportName = "Spritesheet"
        self.exportDir = Path.home() #remember this is a Path, not a string, and as such you can't do string operations on it (unless you convert it first)
        self.rows = 0
        self.columns = 0
        self.start = 0
        self.end = 0
        self.overwrite = False # for now I'm not using it as it could lead to accidentally deleting a folder where the user has important stuff
        # to use it I would need to remove all tmp files (if self.overwrite is true) instead of the tmp folder
        self.removeTmp = True
        self.step = 1
#        if platform.system() == 'Windows':
#            separator = "\\"

    # exporter:
    # export all frames of the animation in a temporary folder as png
    # create a new document of the right dimensions according to self.rows and self.columns
    # position each exported frame in the new doc according to its name
    # export the doc (aka the spritesheet)
    # remove tmp folder if needed
    def export(self, debugging = False):

        # create a temporary export directory for the individual sprites
        tmpFolder = self.exportName + "_sprites" # to be removed when finished # if the user wishes
        tmpName = self.exportName + "_"
        if not self.overwrite:
            exportNum = 0
        
        # in case the user has a folder with the exact same name as my temporary one
            while ((self.exportDir.joinpath(tmpFolder + str(exportNum))).exists()):
                exportNum+=1
    
            tmpFolder += str(exportNum)
    
        # if not self.overwrite, tmpFolder cannot already exist and this will always be called
        if not (self.exportDir.joinpath(tmpFolder)).exists():
            (self.exportDir.joinpath(tmpFolder)).mkdir()
    

        # render animation in a tmp folder
        doc = Krita.instance().activeDocument()

        # check self.end value and if needed input default value
        # self.start's default value is 0 so I don't need to do anything
        if(self.end == 0):
            self.end = doc.fullClipRangeEndTime()
        # give default value to step
        if (self.step == 0):
            self.step = 1 
        doc.setCurrentTime(self.start)
        if(debugging):
            print("animation Length: " + str(doc.animationLength()) + "; full clip self.start: " + str(doc.fullClipRangeStartTime()) + "; full clip self.end: " + str(doc.fullClipRangeEndTime()) + "; playback self.start time: " + doc.playbackStartTime() + "; playback self.end time: " + playbackEndTime())
        framesNum = (self.end - self.start)/self.step
        # it would be better to have the default value be from first to last effective frame instead of asking the user to correctly set the Start and End anim values each time, but as of now krita can't it seems
        doc.setBatchmode(True) # so it won't show the export dialog window    
        tmpNum = 0
        while(doc.currentTime() <= self.end):
            doc.exportImage(str(self.exportDir.joinpath(tmpFolder, tmpName + str(tmpNum).zfill(3) + ".png")), InfoObject())
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
        #print(dir(doc))
    
    
        # getting a default value for rows and columns    
        if (self.rows == 0) and (self.columns == 0):
        # square fit
            self.columns = ceil(sqrt(framesNum))
            self.rows = ceil(float(framesNum)/self.columns)
        # or one row?
        #self.rows = 1
        #self.columns = framesNum
            if (debugging):
                print("self.rows: " + str(self.rows) + "; self.columns: " + str(self.columns))
    
        # if only one is specified, guess the other    
        elif (self.rows == 0):
            self.rows = ceil(float(framesNum)/self.columns)
        # though if I have to guess the number of columns it may also change the (user-set) number of rows
        # for example if you want ten rows from twelve sprites
        # instead of two rows of two and eight of one
        # you'll have six rows of two
        elif (self.columns == 0):
            self.columns = ceil(float(framesNum)/self.rows)
            self.rows = ceil(float(framesNum)/self.columns)
    

        # creating a new document where we'll put our sprites
        sheet = Krita.instance().createDocument(self.columns * width, self.rows * height, self.exportName, col, depth, profile, res)
        if (debugging):
            print("new doc name: " + sheet.name())
            print("old doc width: " + str(width))
            print("num of frames: " + str(framesNum))
            print("new doc width: " + str(sheet.width()))
    
    
        # adding our sprites to the new document
        # and moving them to the right position
        if (debugging):
            print("tmp folder name: " + tmpFolder + ".png")

# for debugging when the result of print() is not available
#        QMessageBox.information(QWidget(), i18n("Debug 130"), i18n("step: " + str(self.step) + "; end: " + str(self.end) + "; start: " + str(self.start) + "; rows: " + str(self.rows) + "; columns: " + str(self.columns)) + "; frames number: " + str(framesNum))
            
            
        imgNum = self.start
        root_node = sheet.rootNode()
        while (imgNum <= self.end):
            img = str(self.exportDir.joinpath(tmpFolder, tmpName + str(imgNum).zfill(3) + ".png"))
            layer = sheet.createFileLayer(img, img, "ImageToSize")
            root_node.addChildNode(layer, None)
            layer.move((((imgNum-self.start)/self.step) % (self.columns)) * width, (int(((imgNum-self.start)/self.step)/self.columns)) * height)
            # I need to merge down each layer or they don't show
            layer.mergeDown()
            if (debugging):
                print("image " + str(imgNum-self.start) + " name: " + img + " at pos:")
                print(layer.position())
            imgNum += self.step
            
        
        # export the document to the export location       
        sheet.setBatchmode(True) # so it won't show the export dialog window
        if debugging:
            print("exporting spritesheet to " + str(self.exportDir.joinpath(self.exportName)))

        sheet.exportImage(str(self.exportDir.joinpath(self.exportName)) + ".png", InfoObject())
        
        # and remove the tmp stuff when you're done
        if debugging:
            print("removing tmp folder " + str(self.exportDir.joinpath(tmpFolder)))
    
        if self.removeTmp:
            rmtree(str(self.exportDir.joinpath(tmpFolder)))
