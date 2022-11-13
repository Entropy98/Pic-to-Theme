import argparse
import copy
import math
import numpy
import subprocess
import sys

from git import Repo
from matplotlib import pyplot as plt
from pathlib import Path
from PIL import Image

WELCOME = "Picture to Unix Theme Utility"

DEFAULT_COLORS = [
        0x000000,   # Black
        0x770000,   # Red
        0x007700,   # Green
        0x777700,   # Yellow
        0x000077,   # Blue
        0x770077,   # Purple
        0x007777,   # Cyan
        0xaaaaaa,   # Gray
        0x555555,   # Dark Gray
        0xcc0000,   # Dark Red
        0x00cc00,   # Dark Green
        0xcccc00,   # Dark Yellow
        0x0000cc,   # Dark Blue
        0xcc00cc,   # Dark Purple
        0x00cccc,   # Dark Cyan
        0xffffff    # White
        ]

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

def print_loading_bar(percentage, length=60):
    '''
    @brief  prints a loading bar at a given percentage. Must be followed by blank print.
    @param  int percentage - percentage complete in the loading bar
    @param  int length - optional parameter for length of loading bar
    '''
    complete_part = '#'*int(percentage/100*length)
    incomplete_part = '.'*(length-(len(complete_part)+1))
    print('\t[{}{}]'.format(complete_part,incomplete_part),end='\r')

def main():
    print(WELCOME)
    parser = argparse.ArgumentParser(description="Script for updating Xrecourses and gnome theme colors based on an image")
    parser.add_argument("image_file", metavar="image_file", type=str, help="path to image file")
    parser.add_argument("-d", "--max-diff", default=100, type=int, help="Maximum difference between colors where they can be considered the same")
    parser.add_argument("-u", "--update-script-name", default="update_theme.sh", type=str, help="Name of the update script generated")
    parser.add_argument("-bg", "--background", default=16, type=int, help="Override the foreground to be the specific color (0-15)")

    args = parser.parse_args()

    img = numpy.asarray(Image.open(args.image_file))

    print("Creating theme from {}".format(args.image_file))
    subprocess.run(["icat",args.image_file])

    max_x = len(img)
    max_y = len(img[0])
    num_colors = len(DEFAULT_COLORS)
    percent_done = 0

    print("Compiling Colors")
    colors = set()
    for x in range(max_x):
        for y in range(max_y):
            percent_done = int(100*(x*max_y+y)/(max_x*max_y))
            print_loading_bar(percent_done)
            colors.add(integerize_color(img[x][y]))
    print("\nDone")

    #Match XTerm colors
    print("Analyzing Colors")
    color_record = [-1]*num_colors
    new_colors = copy.copy(DEFAULT_COLORS)
    color_index = 0
    for color in colors:
        for i in range(num_colors):
            percent_done = int(100*(color_index*num_colors+i)/(len(colors)*num_colors))
            print_loading_bar(percent_done)
            color_diff = compare_colors(seperate_color(DEFAULT_COLORS[i]),seperate_color(color))
            if(color_diff < args.max_diff):
                if(color_record[i] == -1 or color_diff < color_record[i]):
                    color_record[i] = color_diff
                    new_colors[i] = color
        color_index += 1
    print("\nDone")

    color_count = [0]*16
    if((16 > args.background) and (args.background >= 0)):
        bg = new_colors[args.background]
        fg = new_colors[CONTRAST_LUT[args.background]]
    else:
        #Find most used color
        print("Deciding on Background Color")
        for x in range(max_x):
            for i in range(num_colors):
                percent_done = int(100*(x*num_colors+i)/(max_x*num_colors))
                print_loading_bar(percent_done)
                color_count[i] = (img[x] == new_colors[i]).sum()
        greatest_color = color_count.index(max(color_count))
        bg = new_colors[greatest_color]
        fg = new_colors[CONTRAST_LUT[greatest_color]]
        print("\nDone")

    #write .Xresources
    f = open('.Xresources','w')
    f.write('*.foreground: {}\n'.format(colorize_color(fg)))
    f.write('*.background: {}\n'.format(colorize_color(bg)))
    f.write('*.cursorColor: {}\n'.format(colorize_color(fg)))
    for i in range(num_colors):
        f.write("*.color{0}: {1}\n".format(i,colorize_color(new_colors[i])))
    f.close()

    #write gnome terminal script
    f = open(args.update_script_name,'w')
    f.write('#!/bin/bash\n')
    f.write('# This file was automatically generated by Pic2Theme\n')
    f.write('# More information can be found at https://github.com/Entropy98/Pic-to-Theme\n')
    f.write('mv .Xresources ~/\n')
    f.write('xrdb ~/.Xresources\n')
    f.write('i3-msg reload\n')
    f.write('feh --bg-center --no-xinerama {}\n'.format(args.image_file))
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
    print("Xresources updated at home directory. Update theme by executing {}/{}".format(Path.cwd(),args.update_script_name))


if __name__ == '__main__':
    main()
