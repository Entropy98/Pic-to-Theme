import sys
sys.path.append('..')

from pic2theme import *

def test0():
    print("Running Test 0: compare_colors(c1, c2)")
    c1 = [255,0,0]
    c2 = [255,0,0]
    exp_val = 0
    ret_val = compare_colors(c1,c2)
    if(ret_val != exp_val):
        print("compare_colors({0},{1}) returned {2} instead of {3}".format(c1,c2,ret_val,exp_val))
        return

    c1 = [0,255,0]
    c2 = [0,255,0]
    exp_val = 0
    ret_val = compare_colors(c1,c2)
    if(ret_val != exp_val):
        print("compare_colors({0},{1}) returned {2} instead of {3}".format(c1,c2,ret_val,exp_val))
        return

    c1 = [0,0,255]
    c2 = [0,0,255]
    exp_val = 0
    ret_val = compare_colors(c1,c2)
    if(ret_val != exp_val):
        print("compare_colors({0},{1}) returned {2} instead of {3}".format(c1,c2,ret_val,exp_val))
        return

    c1 = [0,0,255]
    c2 = [255,0,0]
    c3 = [0,255,0]
    ret_val1 = compare_colors(c1,c2)
    ret_val2 = compare_colors(c2,c3)
    if(ret_val1 != ret_val2):
        print("compare_colors({0},{1}) and compare_colors({1},{2}) should be equal but are not".format(c1,c2,c3))
        return

    c1 = [50,168,82]
    c2 = [3,66,20]
    c3 = [224, 119, 20]
    ret_val1 = compare_colors(c1,c2)
    ret_val2 = compare_colors(c2,c3)
    if(ret_val1 > ret_val2):
        print("compare_colors({0},{1}) should be less than compare_colors({1},{2}) but is not".format(c1,c2,c3))
        return
    print("Test 0 Passed")

def test1():
    print("Running Test 1: colorize_color(c)")
    c = 0xff0000
    exp_val = "#ff0000"
    ret_val = colorize_color(c)
    if(ret_val != exp_val):
        print("colorize_color({}) should be {} but is {}".format(c,exp_val, ret_val))
        return

    c = 0xabcdef
    exp_val = "#abcdef"
    ret_val = colorize_color(c)
    if(ret_val != exp_val):
        print("colorize_color({}) should be {} but is {}".format(c,exp_val, ret_val))
        return

    c = 0x123456
    exp_val = "#123456"
    ret_val = colorize_color(c)
    if(ret_val != exp_val):
        print("colorize_color({}) should be {} but is {}".format(c,exp_val, ret_val))
        return

    c = 0x00fa00
    exp_val = "#00fa00"
    ret_val = colorize_color(c)
    if(ret_val != exp_val):
        print("colorize_color({}) should be {} but is {}".format(c,exp_val, ret_val))
        return

    print("Test 1 Passed")

def main():
    run_all = False
    if(len(sys.argv) < 2):
        run_all = True

    if(run_all or (sys.argv[1] == '0')):
        test0()
    if(run_all or (sys.argv[1] == '1')):
        test1()

if __name__ == '__main__':
    main()
