#!/usr/bin/python
# -*- coding: utf8 -*-
##
#Copyright 2013 (Jason Wheeler INIT6@INIT6.me) and DC214.org
#
#This file is part of ID-PCB (IRC distributed password cracking bot.)
#
#    ID-PCB is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License.
#
#    ID-PCB is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    To receive a copy of the GNU General Public License
#    see <http://www.gnu.org/licenses/>.
##
############################################

import socket, string, ssl
import urllib, re, os
import shlex
import hashlib

def main():
     
    network = 'irc.init6.me'
    chan = 'pwcrack'
    port = 16667
    sysinfo = readsysinfo()
    for line in sysinfo:
        if re.match("^CID_",line):
            nick = line 
        if re.match("^system\.",line):
            system = line.split('.')[1]
        if re.match("^bits\.",line):
            bits = line.split('.')[1]
        if re.match("^cpuCount\.",line):
            threads = int(line.split('.')[1])
        if re.match("^gpuType\.",line):
            gpu = line.split('.')[1]
        if re.match("^pass\.", line):
            password = line.split('.')[1]
        if re.match("^email\.",line):
            email = '.'.join(line.split('.')[1:])
            
    chan1 = 'pwc'+ '_'.join(nick.split('_')[1:])
    print chan1, nick, system, bits, threads, gpu, password, email

    connect(network, nick, chan, chan1, port, system, bits, threads, gpu, password, email)
    
def readsysinfo():
    try:
        sysinfo = [line.strip('\n') for line in open('sysinfo', 'r')]
        return sysinfo

    except IOError as e:
        print("({0})".format(e))
        
def connect(network, nick, chan, chan1, port, system, bits, threads, gpu, password, email):
    import socket, string, time, ssl
    import urllib, re, os
    from async_subprocess import AsyncPopen, PIPE

    def ircmsg(ircCMD, channel, msg):
        irc.send('%s #%s %s \r\n' % (ircCMD, channel, msg))
    def join(channel):
        irc.send('JOIN #%s \r\n' % channel)
        
    def command(cmd):
        import os
        import time
        import datetime as dt
        
        charset1 = "?l?u?d?s"
        charset2 = "?l?u?d?s?h"
        charset3 = "?l?u?d?s?D"
        charset4 = "?l?u?d?s?F"
        charset5 = "?l?u?d?s?R"
        charset6 = "?l?u?d?s?h?D?F?R"
        
	#split up string into arguments.
	args = shlex.split(cmdline)
        statusKey = '\n'
        whitelist = ["oclHashcat-plus32.exe", "cudaHashcat-Plus32.exe", "oclHashcat-plus64.exe", "cudaHashcat-plus64.exe", \
                     "./oclHashcat-plus32.bin", "./cudaHashcat-Plus32.bin", "./oclHashcat-plus64.bin", "./cudaHashcat-plus64.bin", \
                     "hashcat-cli64.exe", "hashcat-cli32.exe", "./hashcat-cli32.bin", "./hashcat-cli64.bin"]
    
        if str(args[0]) in whitelist:
            if checkhash(args[0]):
                pass
            else:
                print "bad man  is after you"
                exit()
        else:
            exit()
        #Get the file name for the found passwords, and change the status key to 's' if gpu based.
        for arg in args:
            
            if re.search('found', arg):
                foundfile = arg
            if re.search('plus', arg):
                statusKey = 's'
            if re.search('charset', arg):
                if arg == 'charset1':
                    charset = charset1
                    index = args.index(arg)
                    args.remove(arg)
                    args.insert(index, charset)
            
                elif arg == 'charset2':
                    charset = charset2
                    index = args.index(arg)
                    args.remove(arg)
                    args.insert(index, charset)
                    
                elif arg == 'charset3':
                    charset = charset3
                    index = args.index(arg)
                    args.remove(arg)
                    args.insert(index, charset)
                    
                elif arg == 'charset4':
                    charset = charset4
                    index = args.index(arg)
                    args.remove(arg)
                    args.insert(index, charset)

                elif arg == 'charset4':
                    charset = charset4
                    index = args.index(arg)
                    args.remove(arg)
                    args.insert(index, charset)
                    
                elif arg == 'charset5':
                    charset = charset5
                    index = args.index(arg)
                    args.remove(arg)
                    args.insert(index, charset)
                    
                elif arg == 'charset6':
                    charset = charset6
                    index = args.index(arg)
                    args.remove(arg)
                    args.insert(index, charset)
                    
                               
        #excute command
	process = AsyncPopen(args,
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=PIPE
                            )
	retcode = process.poll()
	
	while retcode == None:
            time.sleep(60) #in seconds
	    stdoutdata, stderrdata = process.communicate(statusKey)
	    if stderrdata:
                print stderrdata
	    if stdoutdata:
                data = re.sub(' ', '..', stdoutdata)
                outdata = data.split('\n')
                for line in outdata:
                    if line:
                        if re.search('Speed|Recovered|Progress', line):
                            ircmsg('PRIVMSG', chan1, line)
		
	    #Check if Saturday 8/3/2013 if so Check hour >= 23:35 to kill process and upload found files and exit. 
            date = dt.date.today().isoformat()
            timeMinSec =  '.'.join(str(dt.datetime.today()).split()[1].split(':')[:2])
            if date == '2013-08-03':
		if float(timeMinSec) >=  23.35:
                    print "Time is up, closing and uploading what we have done so far"
                    if statusKey == 's':
                        stdoutdata, stderrdata = process.communicate('q')
                        if os.path.isfile(foundfile):
                            ftpUpload(foundfile, system)
                        process.terminate()
                        return True
                    else:
                        process.terminate()
                        if os.path.isfile(foundfile):
                            ftpUpload(foundfile, system)
                        return True
            else:
                pass
            
	    retcode = process.poll()
        
	#Get found count and upload found file to FTP server.
        if os.path.isfile(foundfile):
            foundCount = getFoundCount(foundfile)
            ftpUpload(foundfile, system)
        else:
            foundCount = 0
            
        trackData = '!TRACK.'+nick+'.completed.'+str(foundCount)
	ircmsg('PRIVMSG', chan1, trackData)
	
	return True 


    socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket.connect((network,port))
    irc = ssl.wrap_socket(socket)
    irc.send('NICK %s\r\n' % nick)
    print irc.recv(4096)
    irc.send('USER %s %s %s :My bot\r\n' % (nick,nick,nick))
    print irc.recv(4096)
    join(chan)
    print irc.recv(4096)
    join(chan1)
    
    state = 'standby'
    msg = '!register.'+nick+'.'+state+'.'+system+'.'+bits+'.'+str(threads)+'.'+gpu+'.'+password+'.'+email
    ircmsg('PRIVMSG', chan, msg)
	
    while True:
        data = irc.recv(4096)
        print data

	if data.find('PING') != -1:
            irc.send('PONG '+data.split()[1]+'\r\n')
	if data.find('!gtfo\r\n') != -1:
            irc.send('QUIT\r\n')
            exit()#exits python.
            
	if data.find('!%s' % (nick) ) != -1:
            cmd = '!'.join(data.split('!')[2:])
            cmdline = ' '.join(cmd.split('..')[1:])

            cmdStatus = command(cmdline)
            if cmdStatus:
                msg1 = '!update.'+nick+'.'+'ready'+'.'+system+'.'+bits+'.'+str(threads)+'.'+gpu+'.'+password+'.'+email
                ircmsg('PRIVMSG', chan1, msg1)
                ircmsg('PRIVMSG', chan, msg1)
            else:
                msg2 = '!update.'+nick+'.'+'error'+'.'+system+'.'+bits+'.'+str(threads)+'.'+gpu+'.'+password+'.'+email
                ircmsg('PRIVMSG', chan1, msg2)
                ircmsg('PRIVMSG', chan, msg2)

            
        if data.find('!GET') != -1:
            output = '!'.join(data.split('!')[2:])
            filename = '.'.join(output.split('.')[1:]).strip('\r\n')
            if ftpDownload(filename, system):
                ftpdownmsg = "%s was downloaded" % filename
                ircmsg('PRIVMSG', chan, ftpdownmsg)
                
        if data.find('!PUSH') != -1:
            output = '!'.join(data.split('!')[2:])
            filename = '.'.join(output.split('.')[1:]).strip('\r\n').strip('\\').strip('/')
            if ftpUpload(filename, system):
                ftpupmsg = "%s was uploaded" % filename
                ircmsg('PRIVMSG', chan, ftpupmsg)

        if data.find('!RESET') != -1:
            state = 'standby'
            msg = '!register.'+nick+'.'+state+'.'+system+'.'+bits+'.'+str(threads)+'.'+gpu+'.'+password+'.'+email
            ircmsg('PRIVMSG', chan, msg)
            
            
        print data



def ftpUpload(filename, system):
    
    from ftplib import FTP_TLS
    import os
    if os.path.isfile(filename):
        
        zipFilename = compressit(filename, system)
        
        ftps = FTP_TLS()
        ftps.connect('pwcrack.init6.me', '21')
        ftps.auth()
        ftps.login('DC214', 'passwordcrackingcontest')
        ftps.prot_p()
        ftps.set_pasv(True)
        local_file = open(zipFilename, 'rb')
        ftps.storbinary('STOR '+zipFilename, local_file)

        print "file %s has been uploaded." % zipFilename
        return True 
    
def ftpDownload(filename, system):
    from ftplib import FTP_TLS
    import os

    ftps = FTP_TLS()
    ftps.connect('pwcrack.init6.me', '21')
    ftps.auth()
    ftps.login('DC214', 'passwordcrackingcontest')
    ftps.prot_p()
    ftps.set_pasv(True)
    local_filename = filename
    with open(local_filename, 'wb') as f:
        def callback(data):
            f.write(data)
        ftps.retrbinary('RETR %s' % filename, callback)
    f.close()

    file_extension = str(filename.split('.')[1])
    
    if file_extension == '7z':
        status = decompressit(local_filename, system)
        if status:
            print "file %s hash been downloaded." % local_filename
    return True
    

def compressit(filename, system):
    from subprocess import Popen, PIPE
    
    zipFilename = str(filename.split('.')[0]) + '.7z'

    if system == 'Windows':
        args = '7za.exe', 'a', zipFilename, filename
    	compressFile = Popen(args, stdout=PIPE)
    	output = compressFile.communicate()[0]

    	if re.search("Everything is Ok", output):
            return zipFilename
    	else:
            print "something went wrong compressing %s" % filenam



    elif system == 'Linux':
	try:
	    args = './7za', 'a', zipFilename, filename

    	    compressFile = Popen(args, stdout=PIPE)
    	    output = compressFile.communicate()[0]

    	    if re.search("Everything is Ok", output):
                return zipFilename
    	    else:
                print "something went wrong compressing %s" % filename
	except:
	    args = '7z', 'a', zipFilename, filename

    	    compressFile = Popen(args, stdout=PIPE)
    	    output = compressFile.communicate()[0]

    	    if re.search("Everything is Ok", output):
                return zipFilename
    	    else:
                print "something went wrong compressing %s" % filename
    
        
def decompressit(zipFilename, system):
    from subprocess import Popen, PIPE

    if system == 'Windows':
        args = '7za.exe', 'x', '-y', zipFilename
    	decompressFile = Popen(args, stdout=PIPE)
    	output = decompressFile.communicate()[0]
    
    	if re.search("Everything is Ok", output):
            return True
    	else:
            print "something went wrong decompressing %s" % zipFilename

    if system == 'Linux':
	try:
	    args = './7za', 'x', '-y', zipFilename
    	    decompressFile = Popen(args, stdout=PIPE)
    	    output = decompressFile.communicate()[0]
    
    	    if re.search("Everything is Ok", output):
        	return True
    	    else:
        	print "something went wrong decompressing %s" % zipFilename
	except:
	    args = '7z', 'x', '-y', zipFilename
    	    decompressFile = Popen(args, stdout=PIPE)
    	    output = decompressFile.communicate()[0]
    
    	    if re.search("Everything is Ok", output):
        	return True
    	    else:
        	print "something went wrong decompressing %s" % zipFilename


def getFoundCount(foundfile):
    with open(foundfile, 'r') as ff:
        fileData = ff.readlines()

    linecount = len(fileData)
    return linecount

def checkhash(fname):
    fname = fname.strip('./')
    mdfsum = (fname, hashlib.md5(open(fname, 'rb').read()).hexdigest())
    mdf = mdfsum[1]
    url = 'http://pwcrack.init6.me/md5/'+fname+'.md5'
    f = urllib.urlopen(url)
    cmd5sum = f.read()
    if mdf == cmd5sum:
	return True
    else:
	return False
    
    

main()
