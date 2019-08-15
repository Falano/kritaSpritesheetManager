# kritaSpritesheetExporter

krita plugin using the Krita python script manager; **requires Krita 4.2.x** or later (currently using the 4.2.0 pre-alpha version, git 325cbf6)

**Exports to a spritesheet** from the animation timeline (using all visible layers) (the spritesheet's number of rows and columns are user-defined; default is Best Fit (trying to form a square))

- **To import a spritesheet** to the animation timeline of a new layer, simply (with your spritesheet open) go to Image > Image Split then (in a new file of the same dimensions as one frame), [File > Import Animation Frames] (https://docs.krita.org/en/user_manual/animation.html#importing-animation-frames)
- **To merge spritesheet**, go to [File > Import Animation Frames] (https://docs.krita.org/en/user_manual/animation.html#importing-animation-frames) and then Tools > Scripts > Export As Spritesheet

<br/>
<br/>

**Installation instructions:**
- **Download the script** using the green "clone or download" button on this page, then clicking "download as zip"
- **Import the plugin into krita**, by either: 
- - opening krita, going to Tools > Scripts > Import Python Plugin, then selecting the zip file you downloaded, and clicking Ok into the next dialog box; or:
- - extracting the .zip and putting both the spritesheetExporter.desktop file and the spritesheetExporter subfolder into the pykrita folder in krita's resources folder (that you can find through Settings > Manage Resources > Open Resources Folder)
- **Restart Krita** if it was open
- **Activate the plugin** by going to Settings > Configure Krita > Python Plugin Manager and checking Spritesheet Exporter (if krita was open, you may need to restart it to see the script in the list, I'm not sure)
- **Restart Krita**
- you can now use it in Tools > Scripts > Export As Spritesheet

<br/>
<br/>

**Warning:** <br/>
While the script is running, avoid switching active window; it might stop the script before completion, thus not creating the final spritesheet and leaving rogue sprite exports (and maybe a sprite export folder, depending on your settings) in your export folder. If this happens, just close the plugin window, remove the unneeded files and try exporting again.
<br/>
<br/>
Check the Manual.html page for more information.
