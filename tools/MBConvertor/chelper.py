#! /usr/bin/python3
# -*- coding: utf-8 -*-

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def printMBCLogo():
    print("""    __  _______  ______                           __            """)
    print("""   /  |/  / __ )/ ____/___  ____ _   _____  _____/ /_____  _____""")
    print("""  / /|_/ / __  / /   / __ \/ __ \ | / / _ \/ ___/ __/ __ \/ ___/""")
    print(""" / /  / / /_/ / /___/ /_/ / / / / |/ /  __/ /  / /_/ /_/ / /    """)
    print("""/_/  /_/_____/\____/\____/_/ /_/|___/\___/_/   \__/\____/_/     """)

def printMBCHelp():
    print(
    """
    Options:
    --startTime, -s     Specify start time of monitoring data           [string]
    --endTime, -e       Specify end time of monitoring data             [string]
    --help, -h          Show help                                       [boolean]
    """)

def printFTFHelp():
    print(
    """
    Options:
    --version, -v       Show version number                             [boolean]
    --hostDetail, -d    Specify hostDetail csv file                     [string]
    --jobDetail, -j     Specify jobDetai csv file                       [string]
    --help, -h          Show help                                       [boolean]
    """)

