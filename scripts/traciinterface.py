#====================================Import Modules====================================
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
import copy	

try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path
.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of \
        your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
from junction import Junction
from device import Device
from phaseConfig import setJunctionPhase

#===============================Generate Route File====================================

#put code to generate route file here, or better make it in some other python file, import and then run here!

#====================================Make Junctions====================================
junction_U = Junction(_id = 'U',
	dev_a_dets = ['0', '1', '2', '3', '4', '5'], 
	dev_b_dets = ['6', '7', '8', '9', '10', '11'], 
	dev_c_dets = ['54', '55', '56', '57', '58', '59'], 
	dev_d_dets = ['60', '61', '62', '63', '64', '65'],
	phaseMap = {1:1, 2:2, 3:4, 4:3})

junction_L = Junction(_id = 'L', 
	dev_a_dets = ['18', '19', '20', '21', '22', '23'], 
	dev_b_dets = ['12', '13', '14', '15', '16', '17'], 
	dev_c_dets = ['66', '67', '68', '69', '70', '71'], 
	dev_d_dets = ['24', '25', '26', '27', '28', '29'],
	phaseMap = {1:1, 2:2, 3:4, 4:3})

junction_R = Junction(_id = 'R', 
	dev_a_dets = ['30', '31', '32', '33', '34', '35'], 
	dev_b_dets = ['48', '49', '50', '51', '52', '53'], 
	dev_c_dets = ['36', '37', '38', '39', '40', '41'], 
	dev_d_dets = ['42', '43', '44', '45', '46', '47'],
	phaseMap = {1:3, 2:1, 3:2, 4:4})

#set neighbours
junction_U.neighbours = [{'junction': junction_L,'connection': ('d', 'b'), 'data':0}, {'junction': junction_R, 'connection': ('c', 'b'), 'data':0}]
junction_L.neighbours = [{'junction': junction_R,'connection': ('c', 'a'), 'data':0}, {'junction': junction_U, 'connection': ('b', 'd'), 'data':0}]
junction_R.neighbours = [{'junction': junction_L,'connection': ('a', 'c'), 'data':0}, {'junction': junction_U, 'connection': ('b', 'c'), 'data':0}]
#========================================run()=========================================
steps = 0
def run():

	global steps
	endSimTIme = 1000
	while steps < endSimTIme:
		
		traci.simulationStep()
		
		runDeviceDetect(time = 20)
		"""
		gets data from devices for
		junctions for "time" number of simulation steps
		"""

		useAlgoAndSetPhase() 
		"""
		use an algorithm to set the phase for the junctions
		"""
		prepareJunctionVectArrs()
		'''
		prepare the vehicleVectarr for junctions
		'''

		setJunctionPhasesInSUMO()
		'''
		set the junction's phases in the SUMO simulator
		'''


		steps += 1
	traci.close()

#==========================Supplimentary functions for run()===========================
def setJunctionPhasesInSUMO():
	setJunctionPhase(junction_U, setAllRed = False)
	setJunctionPhase(junction_L, setAllRed = False)
	setJunctionPhase(junction_R, setAllRed = False)

	return

def useAlgoAndSetPhase():
	
	junction_U.update()
	junction_L.update()
	junction_R.update()
	
	return

def runDeviceDetect(time):
	
	global steps

	for _ in range(time):
		
		junction_U.checkDevices()
		junction_L.checkDevices()
		junction_R.checkDevices()

		traci.simulationStep()
		steps += 1
	
	return 

def prepareJunctionVectArrs():
	
	junction_U.prepareVehVectarr()
	junction_L.prepareVehVectarr()
	junction_R.prepareVehVectarr()
	
	return

#===============================Start SUMO and call run()==============================
def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    #generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "../city.sumocfg",
                             "--tripinfo-output", "../tripinfo.xml"])
    run()
