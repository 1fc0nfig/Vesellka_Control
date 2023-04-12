# Generates an image and sends it to a printer

from PIL import Image, ImageDraw, ImageFont
import time
import os
import random
import argparse

# Open the image file
# image = Image.open('images/blank_2000x1000.png')

# Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mood", help="Name of the mood", required=True)
# parser.add_argument("-i", "--image", help="Path to image", required=True)

# Parse arguments
args = parser.parse_args()

# Select random image from images folder
image = Image.open('images/'+ args.mood + "/" + random.choice(os.listdir('images/' + args.mood)))
print(image)

# Initialize the drawing context
draw = ImageDraw.Draw(image)

# Define the text to be added
# Current date and time in dd.mm.yyyy HH:MM:SS format
text = time.strftime("%d/%m/%Y %H:%M:%S")

# Define the font size and font type
font = ImageFont.truetype("PPMonumentExtended-Regular.ttf", 18)

# Define the text color
color = (20, 20, 20)

# Define the text position
textbbox = draw.textbbox((0, 0), text, font=font)
width, height = image.size
x = ((width - textbbox[2]) / 2 ) - 5
y = ((height - textbbox[3]) / 4)*3 + 60
position = (x, y)

# Add the text to the image
draw.text(position, text, font=font, fill=color)

# get count of files inside the output folder
count = len(os.listdir('output'))

# set filename in format "xxxx_dd_mm_yyyy_HH_MM_SS.png"
filename = str(count).zfill(4) + '_' + time.strftime("%d%m%Y_%H%M%S") + '.png'

# Save the modified image
image.save('output/' + filename)

# print the file
os.system('brother_ql -p usb://0x04f9:0x2042 -m QL-700 print -l 50 output/' + filename)