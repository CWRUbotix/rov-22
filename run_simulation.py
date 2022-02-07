from os import path
import os
import subprocess
from util import ardusub_path, gazebo_path


gazebo_sh = path.join(gazebo_path, 'gazebo.sh')
print(gazebo_sh)
gazebo_process = subprocess.Popen(['bash', '-c', 'source ' + gazebo_sh + ' && gazebo -u worlds/docking_station.world'], cwd=gazebo_path)
ardusub_process = subprocess.Popen(['bash', '-c', 'sim_vehicle.py -f gazebo-bluerov2 --out=udp:0.0.0.0:14550 --console'], cwd=ardusub_path)

while True:
    pass