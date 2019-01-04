# kritaSpritesheetManager

krita plugin using the Krita python script manager; **requires Krita 4.2.* ** or later (currently using the 4.2.0 pre-alpha version, git 325cbf6)

Manages spritesheets; once finished, should contain scripts that:
- **export to a spritesheet** from the animation timeline (using all visible layers) (the spritesheet's number of rows and columns are user-defined; default would be best fit (trying to form a square) or one row, still to be decided)
- **import a spritesheet** to the animation timeline of a new layer (the number of sprites to import and the first frame are user defined; default is all, first frame 0) --TODO--
- **create spritesheets from .png images**, to allow to merge several one-line spritesheets or any number of same-sized images into one spritesheet (default could be one column if not-square input images and best fit otherwise) ---TODO-
