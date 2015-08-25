#!/usr/bin/python
# the above line tells the shell what to invoke this file with
import time
import os
import getpass
import sys

DIR_NAME = '.timers'
TIMER_DIR = '/{}/{}/{}'.format(
                'home'	if sys.platform.startswith('linux')
                        else 'Users'
                , getpass.getuser()
                , DIR_NAME)

# make /Users/<username>/.timers directory
if not os.path.exists(TIMER_DIR):
    os.makedirs(TIMER_DIR)


def print_usage():
    print 'usage: timer.py <timer> [start|stop]'

if __name__ == '__main__':
    # sys.argv is a list of strings: <filename> <timer> <start|stop>
    if len(sys.argv) < 3:
        print_usage()
        exit()

    # check valid command
    if sys.argv[2] not in ('start', 'stop'):
        print_usage()
        exit()

    # get the timer name
    timer = sys.argv[1]
    timer_dir = '{}/{}'.format(TIMER_DIR, timer)
    if sys.argv[2] == 'start':
        start_date = time.strftime("%m/%d/%Y %H:%M:%S")
        # overwrite the timer's file contents with start date and timestamp
        open(timer_dir, 'w').write('{}, {}'.format(start_date, time.time()))
        print 'Timer<{}> started at {}'.format(timer, start_date)

    else:
        # if it doesn't exist then it hasn't been started yet
        if not os.path.exists(timer_dir):
            print 'Timer<{}> does not exist in {}'.format(timer, TIMER_DIR)
            exit()

        # it does exists, so read it and parse
        with open(timer_dir, 'r') as f:
            # start timestamp
            start = float(f.read().split(', ')[1])

            # duration
            dur = int(time.time() - start)

            # divide dur by 60, and mod (%) it by 60
            m, s = divmod(dur, 60)
            h, m = divmod(m, 60)

            # pretty formatting, eh?
            clock = '{}:{}:{}'.format(h, m, s)
            print 'Timer<{}> duration {}'.format(timer, clock)

            # try to remove the file, just stuff the error
            try:
                os.remove(timer_dir)
            except:
                pass
