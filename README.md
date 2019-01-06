# kritaSpritesheetManager

krita plugin using the Krita python script manager; **requires Krita 4.2.* ** or later (currently using the 4.2.0 pre-alpha version, git 325cbf6)

Manages spritesheets; once finished, should contain scripts that:
- **export to a spritesheet** from the animation timeline (using all visible layers) (the spritesheet's number of rows and columns are user-defined; default would be best fit (trying to form a square) or one row, still to be decided)
- **create spritesheets from .png images**, to allow to merge several one-line spritesheets or any number of same-sized images into one spritesheet (default could be one column if not-square input images and best fit otherwise) ---TODO-

- **EDIT:** I also wanted one to **import a spritesheet** to the animation timeline of a new layer, but there actually already are built-in tools:
simply (with your spritesheet open) go to Image > Image Split then (in a new file of the same dimensions as one frame), File > Import Animation Frames
