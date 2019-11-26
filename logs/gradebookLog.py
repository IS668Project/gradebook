import os

from datetime import datetime

def simpleLog(message):
    with open('/home/jsulliv2/gradebook/logs/gradebookLog.log', 'a') as f:
        f.write('{}: {}\n'.format(datetime.utcnow(), message))
    fileSize = os.path.getsize('/home/jsulliv2/gradebook/logs/gradebookLog.log') / 1000000.0 #bytes to MB
    if fileSize > 5:
        with open('/home/jsulliv2/gradebook/logs/gradebookLog.log', 'r') as f:
            text = f.read().splitlines()
            size = len(text)
            replace = text[(int(size/2)):]
        with open('/home/jsulliv2/gradebook/logs/gradebookLog.log', 'w') as f:
            f.write(str(replace))
            f.write('file size surpassed 5 mb, first half of log removed')

if __name__ == '__main__':
    simpleLog('test')