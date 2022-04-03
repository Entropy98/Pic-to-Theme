import sys
import numpy
import math
import copy
from pathlib import Path
from PIL import Image
from matplotlib import pyplot as plt

MAX_DIFF=100

DEFAULT_COLORS = [0x000000, 0x770000, 0x007700, 0x777700, 0x000077, 0x770077, 0x007777, 0xaaaaaa, 0x555555, 0xcc0000, 0x00cc00, 0xcccc00, 0x0000cc, 0xcc00cc, 0x00cccc, 0xffffff]

CONTRAST_LUT = {
        0: 15,
        1: 14,
        2: 13,
        3: 12,
        4: 11,
        5: 10,
        6: 9,
        7: 0,
        8: 15,
        9: 6,
        10: 5,
        11: 4,
        12: 3,
        13: 2,
        14: 1,
        15: 0
        }

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
    for x in range(max_x):
        for y in range(max_y):
            colors.add(integerize_color(img[x][y]))

    #Match XTerm colors
    color_record = [-1]*num_colors
    new_colors = copy.copy(DEFAULT_COLORS)
    for color in colors:
        for i in range(num_colors):
            color_diff = compare_colors(seperate_color(DEFAULT_COLORS[i]),seperate_color(color))
            if(color_diff < MAX_DIFF):
                if(color_record[i] == -1 or color_diff < color_record[i]):
                    color_record[i] = color_diff
                    new_colors[i] = color

    color_count = [0]*16
    #Find most used color
    for x in range(max_x):
        for i in range(num_colors):
            color_count[i] = (img[x] == new_colors[i]).sum()
    greatest_color = color_count.index(max(color_count))
    bg = new_colors[greatest_color]
    fg = new_colors[CONTRAST_LUT[greatest_color]]

    #write .Xresources
    f = open('.Xresources','w')
    f.write('*.foreground: {}\n'.format(colorize_color(fg)))
    f.write('*.background: {}\n'.format(colorize_color(bg)))
    f.write('*.cursorColor: {}\n'.format(colorize_color(fg)))
    for i in range(num_colors):
        f.write("*.color{0}: {1}\n".format(i,colorize_color(new_colors[i])))
    f.close()

    #write gnome terminal script
    f = open('update_gterm.sh','w')
    f.write('#!/bin/bash\n')
    f.write('mv .Xresources ~/\n')
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ palette ")
    f.write('"[')
    for color in new_colors:
        rgb = seperate_color(color)
        f.write("'rgb({},{},{})'".format(rgb[0],rgb[1],rgb[2]))
        if(color != new_colors[-1]):
            f.write(",")
    f.write(']"\n')
    fg_rgb = seperate_color(fg)
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ foreground-color 'rgb({},{},{})'\n".format(fg_rgb[0],fg_rgb[1],fg_rgb[2]))
    bg_rgb = seperate_color(bg)
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ background-color 'rgb({},{},{})'\n".format(bg_rgb[0],bg_rgb[1],bg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ cursor-foreground-color 'rgb({},{},{})'\n".format(fg_rgb[0],fg_rgb[1],fg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ cursor-background-color 'rgb({},{},{})'\n".format(fg_rgb[0],fg_rgb[1],fg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ highlight-background-color 'rgb({},{},{})'\n".format(fg_rgb[0],fg_rgb[1],fg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ highlight-foreground-color 'rgb({},{},{})'\n".format(bg_rgb[0],bg_rgb[1],bg_rgb[2]))


if __name__ == '__main__':
    main()
