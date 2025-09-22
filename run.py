import subprocess
import sys
import time

subprocess.Popen(['flask', 'run'])

time.sleep(1)

url = 'http://127.0.0.1:5000/'

if sys.platform.startswith('win'):
    subprocess.run(['start', url], shell=True)
elif sys.platform.startswith('linux'):
    subprocess.run(['xdg-open', url])
elif sys.platform.startswith('darwin'):
    subprocess.run(['open', url])
else:
    print('Unknown OS')
