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

def printLogo():
    print("""    __  ___     __       _           ____        _ __    __          """)
    print("""   /  |/  /__  / /______(_)_________/ __ )__  __(_) /___/ /__  _____ """)
    print("""  / /|_/ / _ \/ __/ ___/ / ___/ ___/ __  / / / / / / __  / _ \/ ___/ """)
    print(""" / /  / /  __/ /_/ /  / / /__(__  ) /_/ / /_/ / / / /_/ /  __/ /     """)
    print("""/_/  /_/\___/\__/_/  /_/\___/____/_____/\__,_/_/_/\__,_/\___/_/      """)

def printHelp():
    print(
    """
    Options:
        
        --startTime, -s     Specify start time of monitoring data           [string]
        --endTime, -e       Specify end time of monitoring data             [string]
        --interval, -i      Specify time interval of monitoring data        [string]
        --valueType, -t     Specify value type: MAX, MIN, MEAN              [string]
        --outfile, -o       Generate a dataframe CSV file for each requests [boolean]
        --version, -v       Show version number                             [boolean]
        --help, -h          Show help                                       [boolean]
    """)