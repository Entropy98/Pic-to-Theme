import sys
import numpy
import math
import copy
from PIL import Image
from matplotlib import pyplot as plt

MAX_DIFF=100

DEFAULT_COLORS = [0x000000, 0x770000, 0x007700, 0x777700, 0x000077, 0x770077, 0x007777, 0xaaaaaa, 0x555555, 0xcc0000, 0x00cc00, 0xcccc00, 0x0000cc, 0xcc00cc, 0x00cccc, 0xffffff]

def compare_colors(c1, c2):
    '''
    @brief  returns the distance between two points in 3D space where x=red, y=green, and z=blue
    @param  [ 0 < r < 255, 0 < g < 255, 0 < b < 255] c2 - color 2
    @param  [ 0 < r < 255, 0 < g < 255, 0 < b < 255] c2 - color 2
    @return distance between c1 and c2
    '''
    return math.sqrt((c1[0]-c2[0])**2+(c1[1]-c2[1])**2+(c1[2]-c2[2])**2)

def integerize_color(c):
    '''
    @brief  converts a color array into an integer value
    @param  [ 0 < r < 255, 0 < g < 255, 0 < b < 255] c - color
    @return int value - int(0xRRGGBB)
    '''
    return (c[0]<<16)+(c[1]<<8)+(c[2]<<0)

def colorize_color(c):
    '''
    @brief  converts a hex value for a color into a color value
    @param  hex c - 0xRRGGBB
    @return color value - #RRGGBB
    '''
    if(isinstance(c, int) or isinstance(c, numpy.int64)):
        c = hex(c)
    c = c.replace('0x','')
    while(len(c) < 6):
        c = '0'+c
    return '#'+c

def seperate_color(c):
    '''
    @brief  converts integer color into array of RGB values
    @param  int c - int(0xRRGGBB)
    @return  [ 0 < r < 255, 0 < g < 255, 0 < b < 255] c - color
    '''
    red = (c & 16711680) >> 16
    green = (c & 65280) >> 8
    blue = c & 255
    return [red, green, blue]

def main():
    img = numpy.asarray(Image.open(sys.argv[1]))
    max_x = len(img)
    max_y = len(img[0])
    num_colors = len(DEFAULT_COLORS)

    colors = set()
    #flatten image
    for x in range(max_x):
        for y in range(max_y):
            colors.add(integerize_color(img[x][y]))

    color_record = [-1]*num_colors
    new_colors = copy.copy(DEFAULT_COLORS)
    for color in colors:
        for i in range(num_colors):
            color_diff = compare_colors(seperate_color(DEFAULT_COLORS[i]),seperate_color(color))
            if(color_diff < MAX_DIFF):
                if(color_record[i] == -1 or color_diff < color_record[i]):
                    color_record[i] = color_diff
                    new_colors[i] = color

    for color in new_colors:
        print(colorize_color(color))

if __name__ == '__main__':
    main()
