import sys, os
import time
from pyomxplayer import OMXPlayer
import salt.utils.event
import subprocess

DELAY_AFTER_PRESSING_START = .5
DELAY_IN_CHECK_POS = .25
SOCK_DIR = '/var/run/salt/minion'

if len(sys.argv)<=1:
	print "Need a file to play"
	sys.exit()
	


def checkpos():
     p = o.position
     time.sleep(DELAY_IN_CHECK_POS)
     if p == o.position:
         print o.position
         return 'stopped'
     else:
         return "playing"

o = OMXPlayer(sys.argv[1]) #carpenter1.mov #'carp/carp/carpenter1_ge.mov'
os.system('killall cat')
o.play()
time.sleep(DELAY_AFTER_PRESSING_START)

while(1):
	status = checkpos()
	if status == 'stopped':
		o.stop()
		subprocess.Popen(["startx"])
		time.sleep(.4)
		os.system('sudo killall Xorg')
		os.system('cat /dev/urandom > /dev/tty1 &')
		payload = {'data': 'stopped'}
        os.system("""salt-call event.fire_master '{"data": "stopped"}'  'omx'""")
		sys.exit("Stopped")
