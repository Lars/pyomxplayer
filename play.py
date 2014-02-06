import sys
import os
import time
from pyomxplayer import OMXPlayer
import salt.utils.event
import subprocess

from datetime import datetime, timedelta
from dateutil import parse4
import logging
logging.basicConfig(filename='play.log',level=logging.DEBUG)


DELAY_AFTER_PRESSING_START = .5
DELAY_IN_CHECK_POS = .4
SOCK_DIR = '/var/run/salt/minion'

if len(sys.argv) <= 1:
    logging.debug("Need a file to play")
    sys.exit()
logging.info("Attempting to play ", str(sys.argv[1]))


#checks to see if movie is moving or if it's over
def checkpos():
    p = o.position
    time.sleep(DELAY_IN_CHECK_POS)
    if p == o.position:
        logging.info(o.position)
        return 'stopped'
    else:
        return "playing"


def wait_for_starttime(iso_format_starttime):
    try:
        starttime = parser.parse(iso_format_starttime)
        logging.info("Waiting until " + str(starttime))
        while(datetime.now() < starttime):
            time.sleep(.1)
        logging.info("Done waiting")
    except:
        logging.debug("Improperly formatted starttime: was it ISO?")
    return

#load movie and start paused
o = OMXPlayer(sys.argv[1])  # carpenter1.mov 'carp/carp/carpenter1_ge.mov'
logging.info("OMXPlayer is: {}".format(str(o)))
o.pause()

#check to see if there's a starttime, in iso format, in which case wait
if len(sys.argv) <= 2:
    wait_for_starttime(sys.argv[2])

os.system('killall cat')
o.play()
logging.info("Playing")
time.sleep(DELAY_AFTER_PRESSING_START)  # helps prevent instant stopping if computer hangs on start of play

while(1):
    status = checkpos()
    if status == 'stopped':
        o.stop()  # to ensure we don't lock up the machine by leaving omxplayer hanging

        # regain screen if omxplayer has hogged it
        subprocess.Popen(["startx"])
        time.sleep(.4)
        os.system('sudo killall Xorg')

        # restart screen saver
        os.system('cat /dev/urandom > /dev/tty1 &')

        # notify salt master that it's over
        payload = {'data': 'stopped'}
        os.system("""salt-call event.fire_master '{"data": "stopped"}'  'omx'""")
        sys.exit("Stopped")
