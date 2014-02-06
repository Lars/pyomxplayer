import sys
import os
import time
from pyomxplayer import OMXPlayer
import salt.utils.event
import subprocess

from datetime import datetime, timedelta
from dateutil import parser
import pytz
est=pytz.timezone('America/New_York')

# Logging
try:
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # create a file handler
    handler = logging.FileHandler('/home/pi/play.log',mode='a')
    handler.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    logger.addHandler(ch)
except Exception, e:
    logger.error('Failed to open logger', exc_info=True)


DELAY_AFTER_PRESSING_START = .5
DELAY_IN_CHECK_POS = .4
SOCK_DIR = '/var/run/salt/minion'

if len(sys.argv) <= 1:
    logger.debug("Need a file to play")
    sys.exit()
logger.info("Attempting to play {}".format(str(sys.argv[1])))


#checks to see if movie is moving or if it's over
def checkpos():
    p = o.position
    time.sleep(DELAY_IN_CHECK_POS)
    if p == o.position:
        logger.info(o.position)
        return 'stopped'
    else:
        return "playing"


def wait_for_starttime(iso_format_starttime):
    try:
        starttime = parser.parse(iso_format_starttime)
        print (starttime - est.localize(datetime.now())).seconds
        logger.info("It is currently {}".format(str(datetime.now())))
        logger.info("Waiting until {}".format(str(starttime)))
        while(est.localize(datetime.now()) < starttime):
            time.sleep(.1)
        logger.info("Done waiting")
    except Exception, e:
        print "exception"
        print Exception
        print e
        logger.debug("Improperly formatted starttime: was it ISO?")
    return

#load movie and start paused
o = OMXPlayer(sys.argv[1])  # carpenter1.mov 'carp/carp/carpenter1_ge.mov'
logger.info("OMXPlayer is: {}".format(str(o)))
o.pause()

#check to see if there's a starttime, in iso format, in which case wait
if len(sys.argv) >= 3:
    wait_for_starttime(sys.argv[2])

os.system('killall cat')
o.play()
logger.info("Playing")
time.sleep(DELAY_AFTER_PRESSING_START)  # helps prevent instant stopping if computer hangs on start of play

while(1):
    status = checkpos()
    if status == 'stopped':
        logger.info("Stopped.")
        o.stop()  # to ensure we don't lock up the machine by leaving omxplayer hanging

        # regain screen if omxplayer has hogged it
        subprocess.Popen(["startx"])
        time.sleep(.4)
        os.system('sudo killall Xorg')

        # restart screen saver
        os.system('cat /dev/urandom > /dev/tty1 &')

        # notify salt master that it's over
        logger.info('Phoning home')
        payload = {'data': 'stopped'}
        os.system("""salt-call event.fire_master '{"data": "stopped"}'  'omx'""")
        sys.exit("Stopped")
