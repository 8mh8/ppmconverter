# PPM Converter

A small python program to convert ppm formatted images into pixel arrays for displaying on a ledmatrix using Arduino.

## USAGE :

This program expects a ppm file for a 24x24 pixel image exported in ASCII format and dumps array list data for writing with Arduino to a 24x24 ledmatrix.

This program is functional but barely finished and does not have fail safes yet.

It will return unexpected results if used otherwise than with a 24x24 ASCII ppm files which contains exactly :
-1732 lines
-a 4 line header
-values ranging between 0 and 255

At this stage of development :
The program uses a GUI created with appJar.
The user can point to any ppm files.
It will identify the number of colors used and convert the "ppm" index to "arduino" index :
    the ppm is read from top to bottom, left to right.
    the matrix is read from bottom right to top left, by sub-matrixs of 8x8. 9 of them in total.

The program will display the colors in the file in RGB format and two buttons will copy to the clipboard the blocks that can be pasted in the Arduino code to display the pixel art.


## IMPROVEMENTS :


Major :
- Add a fail-safe that tests the file and returns an error if it does not have the correct amount of lines
- Add warning message to gui if process file goes wrong
- See if appJar has a copy/paste built-in function to replace tk clipboard object

Minor :
- Check, clarify and clean the comments
- Replace loop-list creations by list comprehensions when possible
- Replace string concatenation by using .join method instead of + operand
- Add a status bar to display the infos of the files instead of inside the gui
