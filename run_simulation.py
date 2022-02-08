import argparse
import json
import logging
from os import path
import os
from run_gui import parse_args, run_gui
import signal
import subprocess
from util import ardusub_path, gazebo_path

def log_subprocess_output(name):
    def hangle_log(pipe):
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            logging.info('%r: %r', name, line)
    return hangle_log

if __name__ == '__main__':
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description='Run the GUI')
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), help='The simulation configuration file')
    parser.add_argument('-f', '--fullscreen', action='store_true', help='Runs the app in fullscreen mode')
    args = parser.parse_args()

    with args.config as file:
        config = json.load(file)
    
    gui_args = parse_args(config['gui_args'])

    gazebo_sh = path.join(gazebo_path, 'gazebo.sh')
    gazebo_cmd = 'gzserver' if config['headless'] else 'gazebo -u '

    gazebo_process = subprocess.Popen(['bash', '-c', 'source ' + gazebo_sh + ' && ' + gazebo_cmd + ' ' + config['world']], cwd=gazebo_path, stdout=subprocess.PIPE, text=True, preexec_fn=os.setsid)
    ardusub_process = subprocess.Popen(['bash', '-c', 'sim_vehicle.py -f gazebo-bluerov2 --out=udp:0.0.0.0:14550 --console'], cwd=ardusub_path, preexec_fn=os.setsid)

    try:
        run_gui(gui_args)
    except Exception as e:
        print(e)
    
    os.killpg(os.getpgid(gazebo_process.pid), signal.SIGINT)
    os.killpg(os.getpgid(ardusub_process.pid), signal.SIGINT)