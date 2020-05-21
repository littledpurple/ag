#!/usr/bin/env python

import re, os, sys, random, argparse

colors=['\x1b[31m','\x1b[32m','\x1b[33m','\x1b[35m','\x1b[36m','\x1b[90m','\x1b[94m','\x1b[91m','\x1b[92m','\x1b[93m','\x1b[95m','\x1b[96m'] # colors for coloring log
modes, out, outlist, pidcolors = 0, "", [], {} # creating some variables

# arguments parsing
parser = argparse.ArgumentParser(description='Asterisk log search utility. Can search by extension, channel name, can show call log. Highlights the log. ')
g = parser.add_mutually_exclusive_group(required=True)
parser.add_argument('log', nargs='?', default="/var/log/asterisk/full", help='Use custon log file, default - /var/log/asterisk/full', type=str)
g.add_argument('-e', action="store", dest="ext", default="", help="Search by extension",type=str) # -e for extension search
g.add_argument('-c', action="store", dest="chan", default="", help="Search by channel name", type=str) # -c for channel search
g.add_argument('-l', action="store", dest="call", default="", help='Show call log', type=str) # -l to show call log
g.add_argument('-f', action="store", dest="full", default="", help='Full text search', type=str) # -f for full text search
args = parser.parse_args()
# end of arguments parsing

# functions
def search_ext(log, text): # search by extension
    outlist, calls=[], []
    regex='\[\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\]\s[A-Z]*\[\d*\]\[([A-Z]\-[^\]]*)][^\[]*\[([^\]]*)\]\s[A-Za-z]*\(\"([^"]*)\"'
    with open(log) as f:
        for line in f: # itereting through the each row of the log
            if (re.match(regex, line)): # if string mathces regular expression
                string=re.split(regex, line) # split the line into list
                if (text in string[3]): # if extension found in the extension part of the line
                        if not (string[1] in calls): # if call ID is not in list
                            calls.append(string[1]) # appending call ID to list
                            outlist.append([string[1], line.rstrip()]) # appending call ID and full line to the output list
    return(outlist)

def search_chan(log, text): # search by extension
    outlist, calls=[], []
    regex='\[\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\]\s[A-Z]*\[\d*\]\[([A-Z]\-[^\]]*)][^\[]*\[([^\]]*)\]\s[A-Za-z]*\(\"([^"]*)\"'
    with open(log) as f:
        for line in f: # itereting through the each row of the log
            if (re.match(regex, line)): # if string mathces regular expression
                string=re.split(regex, line) # split the line into list
                if (text in string[2]): # if channel found in the channel part of the line
                        if not (string[1] in calls): # if call ID is not in list
                            calls.append(string[1]) # appending call ID to list
                            outlist.append([string[1], line.rstrip()]) # appending call ID and full line to the output list
    return(outlist)
    
def search_call(log, call): # search by call
    outlist=[]
    regex='\[\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\]\s[A-Z]*\[\d*\]\[([A-Z]\-[^\]]*)]'
    with open(log) as f:
        for line in f:
            if re.match(regex,line):
                string=re.split(regex,line)
                if (call.lower() in string[1].lower()):
                    outlist.append(line.rstrip())
    return(outlist)

def search_full(log,text): # full text search function
    outlist=[]
    with open(log) as f:
        for line in f:
            if text in line: # case sensitive search
                outlist.append(line.rstrip())
    return(outlist)

def colorlog(log): # function for log coloring
    global colors
    global pidcolors
    nocolor='\x1b[0m' # reset color
    if ("WARNING" in log): # coloring the whole string if function finds ERROR, NOTICE or WARNING in the string
        log=colors[2] + log + nocolor
        return(log)
    if ("ERROR" in log):
        log=colors[0] + log + nocolor
        return(log)
    if ("NOTICE" in log):
        log=colors[6] + log + nocolor
        return(log)
    regex='\[\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\]\s[A-Z]*\[\d*\]\[([A-Z]\-[^\]]*)]' # searching only strings with apps
    if (not re.match(regex, log)):
        return(log)
    pid=re.split(regex,log)
    if pid[1] in pidcolors: # coloring call ID and remembering it
        pidcol=pidcolors[pid[1]]
    else:
        pidcol=random.choice(colors)
        pidcolors[pid[1]]=pidcol 
    log=re.sub(r'(\[[^\]]*\]\s[A-Z]+\[\d*\]\[)(' + pid[1] + ')', r'\1' + pidcol + r'\2' + nocolor, log)
    log=re.sub(r'([A-Z]{1}[a-z]*\(\")([^"]*)',r'\1' +  colors[3] + r'\2' + nocolor, log)
    log=re.sub(r'(\"\,\s\")([^"]*)', r'\1' + colors[3] + r'\2' + nocolor, log)
    log=re.sub(r'([A-Z][A-Za-z]+)(\(\")', colors[4] + r'\1' + nocolor + r'\2', log)
    return(log)

if (args.ext) != "":
    outlist = search_ext(args.log, args.ext)
    for line in outlist:
        print(colorlog(line[1]))
    quit()
    
if (args.chan) != "":
    outlist = search_ext(args.log, args.chan)
    for line in outlist:
        print(colorlog(line[1]))
    quit()

if (args.call) != "":
    outlist = search_call(args.log, args.call)
    for line in outlist:
        print(colorlog(line))
    quit()

if (args.full) != "":
    outlist = search_full(args.log, args.full)
    for line in outlist:
        print(colorlog(line))
    quit()
