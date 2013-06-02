#!/usr/bin/python


from Tkinter import *
import commands
import re



def getip():
    [status, output] = commands.getstatusoutput('ifconfig ppp0')
    pat = r'inet addr:([\d.]+).*'
    match = re.search(pat, output)
    if match:
        return match.group(1)
    else:
        return 'Unable to get IP'

if __name__=='__main__':
    ip = getip()
    f = open('jango ip', 'w')
    f.write(ip)
    f.close()
    root = Tk()
    w=Label(root, text='Your IP is '+ip)
    w.pack()
    root.mainloop()
