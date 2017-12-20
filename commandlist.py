import os
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

list = ['/clear', '/exit', '/help']
allcommands = ['/clear', '/exit', '/who', '/help', '/del']
avoid = ['', ' ', '/n']
texthelp=bcolors.OKGREEN+"Commands: "+str(allcommands)+"\nTo delete all the message run /del"+bcolors.ENDC
def sendcommand(msg):
    if msg == '/clear':
        os.system('clear')
        return 0, ""
    elif msg ==  '/exit':
        print bcolors.FAIL+"Leaving room..."+bcolors.ENDC
        exit();
    elif msg =='/help':
        print texthelp
        return 0, ""