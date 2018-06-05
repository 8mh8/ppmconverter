'''
mh8 - May 2018

This program expects a ppm file for a 24x24 pixel image exported in ASCII format
and dumps array list data for writing with arduino to a 24x24 ledmatrix

This program is beta. It is barely finished and does not have failsafes.
It will return unexpected results if used otherwise than with a 24x24 ascii ppm files which contains exactly :
-1732 lines
-a 4 line header
-values ranging between 0 and 255

At this stage of development the program reads a ppm files, identifies the number of colors used and converts the "ppm" index to "arduino" index :
the ppm is read from top to bottom, left to right
the matrix is read from bottom right to top left, by sub-matrixs of 8x8. 9 of them in total.
It writes a file using the same name as the ppm file name giving two blocks that can be pasted in the arduino code to display the pixel art.
'''

#import libs
from appJar import gui
from Tkinter import Tk

#create GUI variable
app = gui("PPM Converter", "600x400")
app.setFont(10)
app.setExpand("both")

app.addLabel("title", "Welcome to ppmconverter", colspan=3)
app.setLabelBg("title", "green")

#Get the file
app.addFileEntry("Filename :", colspan=3)
app.setFocus("Filename :")

#Add buttons
def press(button):
    if button == "Exit":
        app.stop()
    elif button == "OK":
        filename = app.getEntry("Filename :")
        process(filename)

app.addButtons(["OK", "Exit"], press, colspan=3)


def process(theFile):
    #Slice name to extract a name to use
    splitName = theFile.split("/")#Split the filename
    theName = splitName[len(splitName)-1]#Keep only the last part
    theName = theName[:-4]#Remove the .ppm at the end

    #create an array to receive the lines from the file
    imageDump = []

    #the 'with' structure will automatically close the file when it reaches the end
    with open(theFile, 'r') as f:
        for line in f:
            imageDump.append(line.rstrip('\n'))#The .rstrip() function will remove all the carriage return characters

    #Remove the 4-line header
    del imageDump[0:4]

    #Create three arrays to receive R, G and B values
    pixelRed, pixelGreen, pixelBlue =  [], [], []

    #Sort the image dump into the three R,G,B arrays
    for i, v in enumerate(imageDump):
        if i % 3 == 0:
            pixelRed.append(v)
        if i % 3 == 1:
            pixelGreen.append(v)
        if i % 3 == 2:
            pixelBlue.append(v)
    pixels = zip(pixelRed, pixelGreen, pixelBlue)

    #Reverse the array as the ledmatrix starts from the bottom right while the ppm starts from the top left
    pixels.reverse()

    #Identify the number of colors
    identifiedColors = []

    for i, v in enumerate(pixels):
        if v == ('0', '0', '0'):
            continue    #don't count black pixels
        if v in identifiedColors:
            continue    #only identify colors once
        else:
            identifiedColors.append(v)



    #Create a dictionary to receive the colors and another for the index
    colors, arduinoIndex = {}, {}

    #Fill the color dictionary with the identified colors from above
    for a in range(len(identifiedColors)):
        colors[a] = identifiedColors[a]

    #This variable is used as a buffer in the mathematical equations below
    y = 0

    #Associate all colored (non-black) pixels with their colors in the index dictionary
    #The KEYS will be the index and the VALUES will be the color number as defined in the color dictionary
    for a in colors:
        for x, v in enumerate(pixels):
            if v == colors[a]:
                #Convert all the ppm index to our specific arduino index
                #These are 9 mathematical equations, one for each 8x8 sub-matrix of the 24x24 led-matrix
                if x%24 >= 0 and x%24 <= 7 and x <= 175:
                    y = (x%24 + (x//24)*8)
                    arduinoIndex[y] = a
                    continue

                elif x%24 >= 8 and x%24 <= 15 and x <= 183:
                    y = (x%24 + 56 + (x//24)*8)
                    arduinoIndex[y] = a
                    continue

                elif x%24 >=16 and x%24 <= 23 and x <= 191:
                    y = (x%24 + 112 + (x//24)*8)
                    arduinoIndex[y] = a
                    continue

                elif x >= 192 and x%24 >= 0 and x%24 <= 7 and x <= 367:
                    y = (x - ((x//24) -8)*16)
                    arduinoIndex[y] = a
                    continue

                elif x >= 200 and x%24 >= 8 and x%24 <= 15 and x <= 375:
                    y = (x + 56 - ((x//24)-8)*16)
                    arduinoIndex[y] = a
                    continue

                elif x >= 208 and x%24 >=16 and x%24 <= 23 and x <= 383:
                    y = (x + 112 - ((x//24)-8)*16)
                    arduinoIndex[y] = a
                    continue

                elif x >= 384 and x%24 >= 0 and x%24 <= 7 and x <= 559:
                    y = (x - ((x//24)-16)*16)
                    arduinoIndex[y] = a
                    continue

                elif x >= 392  and x%24 >= 8 and x%24 <= 15 and x <= 567:
                    y = (x + 56 - ((x//24)-16)*16)
                    arduinoIndex[y] = a
                    continue

                elif x >= 400 and x%24 >=16 and x%24 <= 23 and x <= 575:
                    y = (x + 112 - ((x//24) - 16)*16)
                    arduinoIndex[y] = a
                    continue

                else:
                    print("\Warning : an index in the ppm array was not in range (1-576).\nCheck the ppm file.")

    #Send back some info
    #THIS PART NEEDS A HANDLE TO SCROLL !!
    row=app.getRow()
    app.addLabel("label-filename", "File : " + theName, row, 0)
    app.addLabel("label-colnum", "Colors in the file : " + str(len(identifiedColors)), row, 1)
    app.addLabel("text-pixnum", "Number of pixels to draw : " + str(len(arduinoIndex)), row, 2)


    #This class to create as many lists as we have colors
    class ColorArray:
        def __init__(self, id, color, name, index = None):
            self.id = id
            self.color = color
            self.name = name + str(id)
            self.index_array = [x for x, y in index.items() if y == id] if index else []


    #List comprehension to fill the lists with the values from arduinoIndex dictionary
    result = [ColorArray(id, color, theName, arduinoIndex) for id, color in colors.items()]

    #List the colors in GUI
    for c in result:
        row=app.getRow()
        app.addLabel("label-color" + str(c.id), "Color " + str(c.id)+" : " + str(c.color), row, 0, colspan=2)
        app.addLabel("label-pixels" + str(c.id), "Pixels : " + str(len(c.index_array)), row, 2)

    #Bloc to copy/paste before setup() in Arduino
    row=app.getRow()
    app.addLabel("before-setup", "Copy/Paste this part before your setup():", row, 0, colspan=2)
    app.setLabelBg("before-setup", "red")
    text_setup = "// Pixels " + theName + " :\n"
    for c in result:
        text_setup = text_setup + "const uint16_t PROGMEM %s[] = {" % c.name
        text_setup = text_setup + str(c.index_array)[1:-1] + "};\n"

    #Add copy button
    def press(button):
        if button == "Copy before setup()":
            clipboard = Tk()
            clipboard.withdraw()
            clipboard.clipboard_clear()
            clipboard.clipboard_append(text_setup)
            clipboard.update()
            clipboard.destroy()
    app.addButtons(["Copy before setup()"], press, row, 2)

    #Bloc to copy/paste in loop() in Arduino
    row=app.getRow()
    app.addLabel("in-loop", "Copy/Paste this part in your loop():", row, 0, colspan=2)
    app.setLabelBg("in-loop", "orange")
    text_loop = "// Draw %s :" % theName
    for c in result:
        text_loop = text_loop + "\nfor (int i = 0; i < %d; i++){matrix.setPixelColor(pgm_read_word_near(&%s[i]), %s);}" % (len(c.index_array), c.name, str(c.color).replace("\'", "").replace("(","").replace(")",""))
    text_loop = text_loop + "\nmatrix.show();"
    text_loop = text_loop + "\ndelay(delay_var);"
    text_loop = text_loop + "\nmatrix.fillScreen(0);"

    #Add copy button
    def press(button):
        if button == "Copy to loop()":
            clipboard = Tk()
            clipboard.withdraw()
            clipboard.clipboard_clear()
            clipboard.clipboard_append(text_loop)
            clipboard.update()
            clipboard.destroy()
    app.addButtons(["Copy to loop()"], press, row, 2)


#Launch the GUI
app.go()


'''
Improvements to do :

- Needs a RESET button so we can use the program on multiple PPM files without having to relaunch itp
- Aesthetics :
    - add paddings
    - add a small explanation of what file to use
    - add a handle to scroll the section where the colors are listed : when the ppm is dense in different colors the GUI becomes unreadable
- Refine the code, create functions and call them appropriately
- Replace loop-list creations by list comprehensions when possible
- Replace string concatenation by using .join method instead of + operand
'''
