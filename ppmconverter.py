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

#Point to desired file here
theFile = 'ppm/Papilusion.ppm'

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

#Send back some info
print("\nReading file : " + theFile)
print("\nNumber of colors : " + str(len(identifiedColors)))

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

print("Number of pixels to draw : " + str(len(arduinoIndex)))

#This class to dynamically create as many lists as we have colors
class ColorArray:
    def __init__(self, id, color, name, index = None):
        self.id = id
        self.color = color
        self.name = name + str(id)
        self.index_array = [x for x, y in index.items() if y == id] if index else []

#This slice only works when pointing on my computer.. static code.
theName = theFile[4:-4:1]
print("Using variable name : %s\n" % theName)

#List comprehension to fill the lists with the values from arduinoIndex dictionary
result = [ColorArray(id, color, theName, arduinoIndex) for id, color in colors.items()]

for c in result:
    print("Color %s : %s - Pixels : %d" % (c.id, c.color, len(c.index_array)))

thePlace = "ppm/" + theName

with open(thePlace, 'w') as f:
    f.write("Copy/Paste this part before your setup():\n\n")
    f.write("//Pixels %s\n" % theName)
    for c in result:
        f.write("const uint16_t PROGMEM %s[] = {" % c.name)
        f.write(str(c.index_array)[1:-1])
        f.write("};")
        f.write("\n")

    f.write("\n\nCopy/Paste this part in your loop():\n\n")
    f.write("//Draw %s" % theName)
    for c in result:
        f.write("\nfor (int i = 0; i < %d; i++){matrix.setPixelColor(pgm_read_word_near(&%s[i]), %s);}" % (len(c.index_array), c.name, str(c.color).replace("\'", "").replace("(","").replace(")","")))
    f.write("\nmatrix.show();")
    f.write("\ndelay(delay_var);")
    f.write("\nmatrix.fillScreen(0);")



'''
Improvements to do :

- Gamma correction (in arduino or in this script)!
- Improve slicing / naming of file creations
- Replace loop-list creations by list comprehensions when possible
- Prompt user input for pointing to file
- Make the program graphical using an external lib ?
'''