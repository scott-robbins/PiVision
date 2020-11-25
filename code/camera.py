#!/usr/bin/python
import utils
import time 
import sys
import os

# USEFUL SCRPTING 
snap_img = 'raspistill -t 1 -o im.jpeg' # command to take a picture
stream_vid = 'raspivid -t 0 -w 1280 -h 720 -fps 20 -o - | nc -l -k 1234'
watch_stream = 'mplayer -fps 20 -demuxer h264es ffmpeg://tcp://'


def usage():
	print '[!!]\033[1m\033[31m Incorrect Usage\033[0m[!!]'
	print '$ python camera.py < mode >\n'
	print 'Valid Modes Include: '
	print '\t--setup'
	print '\t--stream'
	print '\t--snap'
	print '\t--still-stream'

def setup():
	# setup the camera config for future usage
	if not os.path.isdir(os.getcwd()+'/.cam'):
		os.mkdir('.cam')
	if not os.path.isfile(os.getcwd()+'/.cam/config.txt'):
		print '[*] No Camera Data Found.'
		if raw_input('Would you like to add a camera? [y/n]: ').upper() == 'Y':
			cam_conf = add_new_camera()
	else:
		cam_conf = load_camera_config()	
	return cam_conf

def add_new_camera():
	config = {}
	cam_ip = raw_input('Enter Camera IP Address: ')
	cam_host = raw_input('Enter Camera Hostname: ')
	cam_pass = raw_input('Enter Password for %s@%s: ' % (cam_host, cam_ip))
	# now add ssh keys to the raspberry pi's authorized keys 
	add_keys = '#!/bin/bash\n'
	add_keys += "sshpass -p '%s' sftp %s@%s:/home/%s/" % (cam_pass, cam_host, cam_ip, cam_host)
	add_keys += " <<< $'put tmp.txt'\n"
	add_keys += "sshpass -p '%s' sftp %s@%s:/home/%s/" % (cam_pass, cam_host, cam_ip, cam_host)
	add_keys += " <<< $'put tmp1.sh'\n"
	# add_keys += 'rm -- "$0"\n' # make script self delete! 
	add_keys += 'rm tmp.txt\n#EOF'
	add_key = '#!/bin/bash\ncat tmp.txt >> /home/%s/.ssh/authorized_keys\n\n#EOF' % cam_host
	os.system('cat ~/.ssh/id_rsa.pub >> tmp.txt')
	open('tmp0.sh', 'wb').write(add_keys)
	open('tmp1.sh','wb').write(add_key)
	# send the bash script over
	os.system('bash tmp0.sh >> /dev/null')
	# Now add the key
	os.system("sshpass -p '%s' ssh %s@%s bash tmp1.sh" % (cam_pass, cam_host, cam_ip))
	os.system('rm tmp.txt tmp1.sh tmp0.sh')
	# WRITE TO CONFIG FILE!
	config['host'] = cam_host
	config['ip'] = cam_ip
	open(os.getcwd()+'/.cam/config.txt', 'wb').write('CAMERA_IP=%s\nCAMERA_HOST=%s\n' % (cam_ip, cam_host))
	return config



def load_camera_config():
	config = {}
	for line in open(os.getcwd()+'/.cam/config.txt','rb').readlines():
		if line.split('=')[0] == 'CAMERA_IP':
			config['ip'] = line.split('=')[1].replace('\n','')
		if line.split('=')[0] == 'CAMERA_HOST':
			config['host'] = line.split('=')[1].replace('\n','')
	print config
	return config



def main():
	completed = False

	# check for a snap_cmd
	if '-snap' in sys.argv or '--snap' in sys.argv:
		completed = True
		cam_info = setup()
		print '[* Snapping Image'
		utils.get_image(cam_info['host'], cam_info['ip'])

	# add new camera
	if '-setup' in sys.argv or '--setup' in sys.argv:
		cam_info = setup()
		completed = True
		print '[*] Testing Camera'
		utils.get_image(cam_info['host'], cam_info['ip'])

	if not completed:	# nothing was done, show usage
		usage()	

if __name__ == '__main__':
	main()
