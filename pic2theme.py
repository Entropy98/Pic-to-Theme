import sys
import numpy
import math
import copy
from PIL import Image
from matplotlib import pyplot as plt

RADIUS=50
NUM_COLORS=16

def compare_colors(c1, c2):
    return math.sqrt((c1[0]-c2[0])**2+(c1[1]-c2[1])**2+(c1[2]-c2[2])**2)

def integerize_color(c):
    return (c[0]<<16)+(c[1]<<8)+(c[2]<<0)

def main():
    img = numpy.asarray(Image.open(sys.argv[1]))
    max_x = len(img)
    max_y = len(img[0])

    colors = [0]*16777215
    #flatten image
    for x in range(max_x):
        for y in range(max_y):
            colors[integerize_color(img[x][y])] += 1

    greatest_values = copy.copy(colors)
    greatest_values.sort(reverse=True)
    greatest_colors = []
    colors_found = 0
    for value in greatest_values:
        if(colors_found > NUM_COLORS):
            break
        color = colors.index(value)
        greatest_colors.append(hex(color))
        colors_found += 1
    for color in greatest_colors:
        print(color.replace('0x','#'))

if __name__ == '__main__':
    main()
