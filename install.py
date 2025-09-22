import subprocess
import sys

command = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']

try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    print(f'Error: {e}')
