import argparse
import json
from os import path
import os
from run_gui import parse_args, run_gui
import signal
import subprocess
from util import ardusub_path, config_parser, gazebo_path

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''Run the GUI with Gazebo Simulation. The config file be a JSON file with 3 fields.
            world: A string indicating the gazebo world to run.
            headless: A boolean. If true, gazebo will run without the GUI. If flase, gazebo will run with the GUI.
            gui_args: An array of strings for the arguments passed to run_gui.py
            ''', formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-c', '--config', type=config_parser('simulation'), help='The simulation configuration file located in config/simulation', required=True)
    parser.add_argument('-f', '--fullscreen', action='store_true', help='Runs the app in fullscreen mode')
    args = parser.parse_args()

    with args.config as file:
        config = json.load(file)
    
    gui_args = parse_args(config['gui_args'])
    if args.fullscreen:
        gui_args.fullscreen = True

    gazebo_sh = path.join(gazebo_path, 'gazebo.sh')
    gazebo_cmd = 'gzserver' if config['headless'] else 'gazebo -u '

    gazebo_process = subprocess.Popen(['bash', '-c', 'source ' + gazebo_sh + ' && ' + gazebo_cmd + ' ' + config['world']], cwd=gazebo_path, stdout=subprocess.PIPE, text=True, preexec_fn=os.setsid)
    ardusub_process = subprocess.Popen(['bash', '-c', 'sim_vehicle.py -f gazebo-bluerov2 --out=udp:0.0.0.0:14550 --console'], cwd=ardusub_path, preexec_fn=os.setsid)

    # Unfortunately, pyqt does not handle keyboard interrupts, so using ctrl-c on this script will kill it without being able to clean up subprocesses.
    try:
        run_gui(gui_args)
    except Exception as e:
        print(e)
    
    # Use interrupt signal instead of kill, otherwise ArduSub and Gazebo do not clean up all their subprocesses.
    os.killpg(os.getpgid(gazebo_process.pid), signal.SIGINT)
    os.killpg(os.getpgid(ardusub_process.pid), signal.SIGINT)