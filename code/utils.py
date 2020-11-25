from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
try:
	import paramiko
	MIKO = True
except ImportError:
	print '[!!] Cannot use Paramiko'
	MIKO = False
import warnings
import base64
import socket
import time
import sys 
import os
                                       # SUPRESSING PARAMIKO WARNINGS!
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

def swap(filename, destroy):
	data = []
	for line in open(filename, 'rb').readlines():
		data.append(line.replace('\n', ''))
	if destroy:
		os.remove(filename)
	return data

def arr2str(content):
	result = ''
	for element in content:
		result += element + '\n'
	return result

def arr2chstr(content):
	result = ''
	for element in content:
		result += element + ' '
	return result

def get_ext_ip():
	return cmd('curl -s https://api.ipify.org',False).pop()

def create_timestamp():
	date = time.localtime(time.time())
	mo = str(date.tm_mon)
	day = str(date.tm_mday)
	yr = str(date.tm_year)

	hr = str(date.tm_hour)
	min = str(date.tm_min)
	sec = str(date.tm_sec)

	date = mo + '/' + day + '/' + yr
	timestamp = hr + ':' + min + ':' + sec
	return date, timestamp

def cmd(command, verbose):
	os.system('%s >> cmd.txt' % command)
	if verbose:	
		os.system('cat cmd.txt')
	return swap('cmd.txt', True)

def ssh_exec(c,addr,hostname,verbose):
	 return cmd('ssh %s@%s %s' % (hostname,addr, c), verbose)

def ssh_get_file(r_path, rmt_file, ip, uname):
	# TODO: Add no Miko error handling
	cmd = 'sftp %s@%s:%s/%s' % (uname, ip, r_path,rmt_file)
	os.system(cmd)
	return True

def ssh_get_file_del(r_path, rmt_file, ip, uname):
	# Function for getting file and deleting remote copy in one command
	cmd_get = 'sftp %s@%s:%s/%s; ' % (uname, ip, r_path,rmt_file)
	cmd_del_a = 'ssh %s@%s ' % (uname, ip)
	cmd_del_b = "'rm %s/%s'" % (r_path, rmt_file)
	cmd_full = cmd_get + cmd_del_a + cmd_del_b
	deleted = False
	try:
		os.system(cmd_full)
		deleted = True
	except OSError:
		pass
	return deleted	

def ssh_put_file(localfile, rpath, ip, uname):
	# TODO: Add no Miko error handling
	cmd1 = 'sftp %s@%s:%s' % (uname,ip,rpath)
	cmd2 = " <<< $'put %s'" % (localfile)
	getreq = cmd1+cmd2
	open('tmp.sh','wb').write('#!/bin/bash\n%s\n#EOF'%getreq)
	os.system('bash tmp.sh >> /dev/null')
	os.remove('tmp.sh')
	return True

def get_image(hname, ip):
	ssh_exec('raspistill -t 1 -o a.jpeg',ip,hname,False)
	ssh_get_file_del('/home/pi','a.jpeg',ip,hname)
	now = np.array(plt.imread('a.jpeg'))
	plt.imshow(now)
	plt.show()
	os.remove('a.jpeg')
	return now
