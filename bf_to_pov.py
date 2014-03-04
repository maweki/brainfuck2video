#!/usr/bin/env python3

from __future__ import print_function
import os
import sys
import errno
import time
import datetime
import argparse
import array
import math
import multiprocessing
import tempfile
import shutil
from time import sleep


def main():
	parser = argparse.ArgumentParser(description='Converts brainfuck code to povray scene')
	parser.add_argument('--fps', metavar='frames_per_second', type=int, default=24)
	parser.add_argument('--fpt', metavar='frames_per_tick', type=int, default=48)
	parser.add_argument('--mt', metavar='maxticks', type=int, default=300)
	parser.add_argument('--width', metavar='width', default='640')
	parser.add_argument('--height', metavar='height', default='480')
	parser.add_argument('--bitrate', metavar='bitrate', default='4000K')
	parser.add_argument('--dontrender', action='store_const', const=True)
	try:
		cpus = multiprocessing.cpu_count()*2
	except:
		cpus = 2
	parser.add_argument('--threads', metavar='threads', type=int, default=cpus)
	parser.add_argument('--input', metavar='inputfile', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
	parser.add_argument('codefile', metavar='codefile', type=file)
	parser.add_argument('outputfile', metavar='outputfile')
	args = parser.parse_args()

	bf_commands = ['+', '-', '.', ',', '>', '<', '[', ']']

	max_bf_array_size = 1000
	bf_pointer_before_tick = bf_pointer_after_tick = 0
	bf_array_before_tick = array.array('b')
	bf_array_after_tick = array.array('b')
	for i in range(max_bf_array_size):
		bf_array_before_tick.append(0)
		bf_array_after_tick.append(0)
	loop_depth = 0
	codepos_before_tick = codepos_after_tick = 0
	ticks=0

	code = ''
	code_raw = args.codefile.read()
	for c in code_raw:
		if c in bf_commands:
			code = code + c
	print(code)

	scene_amb = '#include "scene_def.pov.inc"\n'
	scene_amb = scene_amb + '#declare code="'+code+'";\n'
	scene_amb = scene_amb + '#switch (clock)\n'
	scene_int = ''

	while codepos_after_tick < len(code) and ticks < args.mt:
		if code[codepos_before_tick] in bf_commands:
			ticks = ticks + 1

		c  = code[codepos_before_tick]

		# non flow-control-characters
		if c in bf_commands[:6]:
			codepos_after_tick = codepos_after_tick + 1

		# +
		if c in bf_commands[0]:
			bf_array_after_tick[bf_pointer_before_tick] = bf_array_after_tick[bf_pointer_before_tick] + 1

		# -
		if c in bf_commands[1]:
			bf_array_after_tick[bf_pointer_before_tick] = bf_array_after_tick[bf_pointer_before_tick] - 1

		# >
		if c in bf_commands[4]:
			bf_pointer_after_tick = bf_pointer_after_tick + 1

		# <
		if c in bf_commands[5]:
			bf_pointer_after_tick = bf_pointer_after_tick - 1

		#control flow
		if c in bf_commands[6]:
			# [
			loop_depth = loop_depth + 1
			if bf_array_after_tick[bf_pointer_before_tick] > 0:
				codepos_after_tick = codepos_after_tick + 1
			else:
				t_loop = loop_depth - 1
				while (t_loop != loop_depth):
					codepos_after_tick = codepos_after_tick + 1
					if code[codepos_after_tick] in bf_commands[6]:
						t_loop = t_loop + 1
					if code[codepos_after_tick] in bf_commands[7]:
						t_loop = t_loop - 1
				

		if c in bf_commands[7]:
			# ]
			loop_depth = loop_depth - 1
			if bf_array_after_tick[bf_pointer_before_tick] == 0:
				codepos_after_tick = codepos_after_tick + 1
			else:
				t_loop = loop_depth + 1
				while (t_loop != loop_depth):
					codepos_after_tick = codepos_after_tick - 1
					if code[codepos_after_tick] in bf_commands[6]:
						t_loop = t_loop - 1
					if code[codepos_after_tick] in bf_commands[7]:
						t_loop = t_loop + 1
		#add to scene

		this_tick = ''

		scene_int = scene_int + '#range ('+str(ticks-1)+'.0,'+str(ticks)+'.0)\n';
		this_tick = this_tick + '#declare intclock = clock-'+str(ticks-1)+'.0;\n';
		this_tick = this_tick + '#declare code_from = '+str(codepos_before_tick)+';\n';
		this_tick = this_tick + '#declare code_to = '+str(codepos_after_tick)+';\n';
		this_tick = this_tick + '#include "code.pov.inc"\n';

		this_tick = this_tick + '#declare sl_pos_from = '+str(bf_pointer_before_tick)+';\n';
		this_tick = this_tick + '#declare sl_pos_to = '+str(bf_pointer_after_tick)+';\n';
		this_tick = this_tick + '#include "camandlight.pov.inc"\n';
		
		for i in range(max_bf_array_size):
			if (bf_array_before_tick[i] > 0) or (bf_array_after_tick[i] > 0):
				this_tick = this_tick + '#declare boxpos = '+str(i)+';\n';
				this_tick = this_tick + '#declare boxvalue_from = '+str(bf_array_before_tick[i])+';\n';
				this_tick = this_tick + '#declare boxvalue_to = '+str(bf_array_after_tick[i])+';\n';
				this_tick = this_tick + '#include "box.pov.inc"\n';
		scene_int = scene_int + this_tick		
		scene_int = scene_int + '#break\n';
		
		
		#equalize variables
		codepos_before_tick = codepos_after_tick
		bf_pointer_before_tick = bf_pointer_after_tick
		for i in range(max_bf_array_size):
			bf_array_before_tick[i] = bf_array_after_tick[i]

	scene_int = scene_int + '#else\n'
	scene_int = scene_int + this_tick
	scene_int = scene_int + '#end\n'

	print(ticks, " ticks with ", args.fpt , " frames per tick and ", args.fps, " frames per second ")
	print((ticks*args.fpt), " frames in " ,(ticks*args.fpt/args.fps), " seconds")
	if args.dontrender:
		print(scene_int)
		quit()

	answer = ''
	answer = raw_input("Continue to render in " + str(args.threads) + " Threads? yes/no\n")

	if answer != 'yes':
		quit()

	tmppath = tempfile.mkdtemp();
	sceneprefix = 'scene_'
	scenefile = tmppath + os.sep + sceneprefix + '.pov'

	f = open(scenefile, 'w')
	f.write(scene_amb + scene_int)
	f.close()

	processes = array.array('I')
	part = (ticks*args.fpt) / args.threads

		

	for i in range(args.threads):
		processes.append(os.spawnlp(os.P_NOWAIT, 'povray', '+Lscene', '+Q8', '+A', '-V', '-GD', '-GR', '-GS', '-GA', '-D', '+KI0.0', '+O'+tmppath+os.sep,'+KF' + str(ticks) + '.0', '+KFF' + str(ticks*args.fpt) , '+SF'+str(math.trunc(i*part)+1), '+EF'+str(math.trunc((1+i)*part)), '+H' + args.height, '+W' + args.width, scenefile))

	for i in processes:
		os.waitpid(i,0)
	
	print(ticks, " ticks with ", args.fpt , " frames per tick and ", args.fps, " frames per second ")
	print((ticks*args.fpt), " frames in " ,(ticks*args.fpt/args.fps), " seconds")

	print("Beginning concatenating to video")

	imgprefix = tmppath + os.sep + sceneprefix
	
	sleep(5)	

	#ffmpegpid = os.spawnlpe(os.P_NOWAIT, 'ffmpeg', '-r', args.fps, '-b', args.bitrate, '-i', imgprefix+'%0'+str(len(str(ticks*args.fpt)))+'d.png', imgprefix+'.mp4')
	#os.waitpid(ffmpegpid,0)
	
	ffmpegscript = 'ffmpeg -r '+str(args.fps)+' -i '+imgprefix+'%0'+str(len(str(ticks*args.fpt)))+'d.png '+' -b '+str(args.bitrate)+' '+imgprefix+'.mp4'+'\n'#+'mv '+imgprefix+'.mp4'+' '+args.outputfile
	print(ffmpegscript)
	ff = open(imgprefix+'.sh', 'w')
	ff.write(ffmpegscript)
	ff.close
	#print('ffmpeg', '-r', args.fps, '-b', args.bitrate, '-i', imgprefix+'%0'+str(len(str(ticks*args.fpt)))+'d.png', imgprefix+'.mp4')
	
	
	os.spawnlpe(os.P_WAIT, 'sh', imgprefix+'.sh')

	#shutil.move(imgprefix+'.mp4', args.outputfile)
	

if __name__ == '__main__':
    main()
