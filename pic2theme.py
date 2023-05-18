import argparse
import copy
import math
import numpy
import subprocess

from pathlib import Path
from PIL import Image
from typing import Dict, List, Set, Tuple

from color_types import AnsiColor, ColorString, ColorList, HexColor, Img, ImgPath, RGBVal

WELCOME: str = "Picture to Unix Theme Utility"

NUM_COLORS: int = 16
DEFAULT_COLORS: ColorList = [
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

CONTRAST_LUT: Dict = {
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

ANSICOLORS: List[AnsiColor] = [
        "\u001b[30m",
        "\u001b[31m",
        "\u001b[32m",
        "\u001b[33m",
        "\u001b[34m",
        "\u001b[35m",
        "\u001b[36m",
        "\u001b[37m",
        "\u001b[30;1m",
        "\u001b[31;1m",
        "\u001b[32;1m",
        "\u001b[33;1m",
        "\u001b[34;1m",
        "\u001b[35;1m",
        "\u001b[36;1m",
        "\u001b[37;1m",
        ]
ANSICOLOR_RESET: AnsiColor = "\u001b[0m"


def compare_colors(c1: RGBVal, c2: RGBVal) -> int:
    '''
    @brief  returns the distance between two points in 3D space where x=red, y=green, and z=blue
    @param  RGBVal c2 - color 2
    @param  RGBVal c2 - color 2
    @return distance between c1 and c2
    '''
    return math.sqrt((c1[0]-c2[0])**2+(c1[1]-c2[1])**2+(c1[2]-c2[2])**2)


def integerize_color(c: RGBVal) -> HexColor:
    '''
    @brief  converts a color array into an integer value
    @param  RGBVal c - color
    @return HexColor value - int(0xRRGGBB)
    '''
    return (c[0] << 16)+(c[1] << 8)+(c[2] << 0)


def colorize_color(c: HexColor | numpy.int64) -> ColorString:
    '''
    @brief  converts a hex value for a color into a color value
    @param  hex c - 0xRRGGBB
    @return ColorString value - #RRGGBB
    '''
    if (isinstance(c, int) or isinstance(c, numpy.int64)):
        c = hex(c)
    c = c.replace('0x', '')
    while (len(c) < 6):
        c = '0'+c
    return '#'+c


def seperate_color(c: HexColor) -> RGBVal:
    '''
    @brief  converts integer color into array of RGB values
    @param  int c - int(0xRRGGBB)
    @returns RGBVal c - color
    '''
    red: RGBVal = (c & 16711680) >> 16
    green: RGBVal = (c & 65280) >> 8
    blue: RGBVal = c & 255
    return [red, green, blue]


def print_loading_bar(percentage: int, length=60) -> None:
    '''
    @brief  prints a loading bar at a given percentage. Must be followed by blank print.
    @param  int percentage - percentage complete in the loading bar
    @param  int length - optional parameter for length of loading bar
    '''
    complete_part: str = '#'*int(percentage/100*length)
    incomplete_part: str = '.'*(length-(len(complete_part)+1))
    print(f"\t[{complete_part}{incomplete_part}]", end='\r')


def display_image(img: ImgPath) -> None:
    '''
    @brief prints out an image terminal
    @param img - image to display
    '''
    subprocess.run(["imgcat", img])


def compile_colors(img: Img) -> Set[HexColor]:
    '''
    @brief determines which colors from the image should go into the 16 color list
    @param Img img - image to parse
    @returns Set of every color in the image
    '''
    percent_done: int = 0
    max_x: int = len(img)
    max_y: int = len(img[0])

    print("Compiling Colors")
    colors: Set[HexColor] = set()
    for x in range(max_x):
        for y in range(max_y):
            percent_done = int(100*(x*max_y+y)/(max_x*max_y))
            print_loading_bar(percent_done)
            colors.add(integerize_color(img[x][y]))
    print("\nDone")
    return colors


def analyze_colors(colors: Set[HexColor]) -> Tuple[ColorList, List[int]]:
    '''
    @brief determines the foreground and background based on the prominance of colors in the image
    @param Set[HexColor] colors - colors to fit into a 16 color list
    @returns (16 color list, list of color occurances)
    '''
    percent_done: int = 0

    print("Analyzing Colors")
    color_record: List[int] = [-1]*NUM_COLORS
    color_prominence: List[int] = [0]*NUM_COLORS
    new_colors: ColorList = copy.copy(DEFAULT_COLORS)
    color_index: int = 0
    for color in colors:
        for i in range(NUM_COLORS):
            percent_done = int(100*(color_index*NUM_COLORS+i)/(len(colors)*NUM_COLORS))
            print_loading_bar(percent_done)
            color_diff: int = compare_colors(seperate_color(DEFAULT_COLORS[i]), seperate_color(color))
            if (color_diff < args.max_diff):
                color_prominence[i] = color_prominence[i] + 1
                if (color_record[i] == -1 or color_diff < color_record[i]):
                    if (args.verbose >= 5):
                        print(f"Found better {ANSICOLORS[i]}{colorize_color(DEFAULT_COLORS[i])}{ANSICOLOR_RESET}! New color is {ANSICOLORS[i]}{colorize_color(color)}{ANSICOLOR_RESET}")
                    color_record[i] = color_diff
                    new_colors[i] = color
        color_index += 1
    print("\nDone")
    return (new_colors, color_prominence)


def determine_background(colors: ColorList, prominance: List[int], bg_override: int) -> Tuple[HexColor, HexColor]:
    '''
    @brief determines the background color based on the prominance of colors in the image
    @param ColorList colors - 16 color list based on img
    @param int bg_override - color in 16 color list to set color to
    @returns tuple(bg, fg) of the background and foreground
    '''
    bg: HexColor = DEFAULT_COLORS[0]
    fg: HexColor = DEFAULT_COLORS[7]

    if ((16 > bg_override) and (bg_override >= 0)):
        if (args.verbose >= 1):
            print(f"Background Override Enabled... Using {colorize_color(colors[bg_override])}")
        bg = colors[bg_override]
        fg = colors[CONTRAST_LUT[bg_override]]
    else:
        greatest_color = prominance.index(max(prominance))
        if (args.verbose >= 2):
            print(f"\nMaking {ANSICOLORS[greatest_color]}{colorize_color(colors[greatest_color])}{ANSICOLOR_RESET} the background because it is the most prevalent")
        if (args.verbose >= 3):
            print("Color Rankings:")
            for i in range(NUM_COLORS):
                print(f"\t{ANSICOLORS[i]}{colorize_color(colors[i])}{ANSICOLOR_RESET}:{prominance[i]}")
        bg = colors[greatest_color]
        fg = colors[CONTRAST_LUT[greatest_color]]
        print("\nDone")

    return (bg, fg)


def compile_xresources(bg: HexColor, fg: HexColor, colors: ColorList) -> None:
    '''
    @brief writes Xresources file
    @param HexColor bg - background color
    @param HexColor fg - foreground color
    @param ColorList colors - 16 color list
    '''
    f = open(".Xresources", 'w')
    f.write("*.foreground: {}\n".format(colorize_color(fg)))
    f.write("*.background: {}\n".format(colorize_color(bg)))
    f.write("*.cursorColor: {}\n".format(colorize_color(fg)))
    for i in range(NUM_COLORS):
        f.write("*.color{0}: {1}\n".format(i, colorize_color(colors[i])))
    f.close()


def compile_update_script(bg: HexColor, fg: HexColor, colors: ColorList) -> None:
    '''
    @brief creates the update script to apply the theme changes
    @param HexColor bg - background color
    @param HexColor fg - foreground color
    @param ColorList colors - 16 color list
    '''
    f = open(args.update_script_name, 'w')
    f.write('#!/bin/bash\n')
    f.write('# This file was automatically generated by Pic2Theme\n')
    f.write('# More information can be found at https://github.com/Entropy98/Pic-to-Theme\n')
    f.write('mv .Xresources ~/\n')
    f.write('xrdb ~/.Xresources\n')
    f.write('i3-msg reload\n')
    f.write('feh --bg-center --no-xinerama {}\n'.format(args.image_file))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ palette ")
    f.write('"[')
    for color in colors:
        rgb = seperate_color(color)
        f.write("'rgb({},{},{})'".format(rgb[0], rgb[1], rgb[2]))
        if (color != new_colors[-1]):
            f.write(",")
    f.write(']"\n')
    fg_rgb = seperate_color(fg)
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ foreground-color 'rgb({},{},{})'\n".format(fg_rgb[0], fg_rgb[1], fg_rgb[2]))
    bg_rgb = seperate_color(bg)
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ background-color 'rgb({},{},{})'\n".format(bg_rgb[0], bg_rgb[1], bg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ cursor-foreground-color 'rgb({},{},{})'\n".format(fg_rgb[0], fg_rgb[1], fg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ cursor-background-color 'rgb({},{},{})'\n".format(fg_rgb[0], fg_rgb[1], fg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ highlight-background-color 'rgb({},{},{})'\n".format(fg_rgb[0], fg_rgb[1], fg_rgb[2]))
    f.write("gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:ad573cac-cd69-44d4-9713-7526db576454/ highlight-foreground-color 'rgb({},{},{})'\n".format(bg_rgb[0], bg_rgb[1], bg_rgb[2]))
    print("Xresources updated at home directory. Update theme by executing {}/{}".format(Path.cwd(), args.update_script_name))


if __name__ == '__main__':
    print(WELCOME)
    parser = argparse.ArgumentParser(description="Script for updating Xrecourses and gnome theme colors based on an image")
    parser.add_argument("image_file", metavar="image_file", type=str, help="path to image file")
    parser.add_argument("-d", "--max-diff", default=100, type=int, help="Maximum difference between colors where they can be considered the same")
    parser.add_argument("-u", "--update-script-name", default="update_theme.sh", type=str, help="Name of the update script generated")
    parser.add_argument("-bg", "--background", default=16, type=int, help="Override the foreground to be the specific color (0-15)")
    parser.add_argument("-v", "--verbose", action="count", default=0)

    args = parser.parse_args()

    img: Img = numpy.asarray(Image.open(args.image_file))

    print(f"Creating theme from {args.image_file}")
    display_image(ImgPath(args.image_file))

    colors: Set[HexColor] = compile_colors(img)
    new_colors: ColorList
    color_prominence: List[int]
    new_colors, color_prominence = analyze_colors(colors)

    bg: HexColor
    fg: HexColor
    bg, fg = determine_background(new_colors, color_prominence, args.background)
    compile_xresources(bg, fg, new_colors)
    compile_update_script(bg, fg, new_colors)
