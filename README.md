# WBSScreenSaver-decoder
Stego tool used to decode a message inside a video where it is encoded inside the color switches

# How it works

This tool is focus on the decoding of information from a videofile where the hidden data is encoded in the color switches. The color switches are from the elemental ones of the RGB spectrum. When the color shifts to the right (From red to green, green to blue or blue to red) it gets the info as a 1, when the shift is to  the left, it gets the info as a 0.

# Pre-requirements

You must have installed python 3.X, numpy and opencv

# How to run it

The tool has several features to configure the way the message is decoded. The arguments are the next ones:
+ -i: Video file to process
+ -X: Position of capture rectangle (horizontal, top-left corner)
+ -Y: Position of capture rectangle (vertical, top-left corner)
+ -W: Width of capture rectangle
+ -H: Height of capture rectangle
+ -s: Minimum HSV saturation of analyzed pixels (0-255)
+ -v: Minimum HSV brightness of analyzed pixels (0-255)
+ -r: Coefficient applied to red component (0-1)
+ -g: Coefficient applied to green component (0-1)
+ -b: Coefficient applied to blue component (0-1)
+ -c: Minimum percentage of pixels in mask relative to capture area (0-100)
+ -f: Minimum number of frames with same color to register a change
+ -F: Display video feedback
+ -d: Enable debugging
+ -h: Help argument

To run the command, you have to run the tool.py file setting at least the argument for the video file and rectangle position and size (-X, -Y, -W and -H). With all this arguments setted, you can run the command. It is recomended to make the first runs with the command -f to be able to see where the rectangle is and know how it is decoding the information.
