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

class bf(object):
	bf_commands = '+-.,><[]'
	max_bf_array_size = 30000

	code = None
	scene = None

	@staticmethod
	def clean_text(text):
		return ''.join(c for c in text if c in bf.bf_commands)

	@staticmethod
	def from_text(text):
		return bf(bf.clean_text(text))

	@staticmethod
	def from_file(fp):
		code_raw = fp.read()
		return bf.from_text(code_raw)

	def scene_amb(self):
		pass

	@staticmethod
	def get_scene_data(code):

		def is_correct_brackets(code):
			depth = 0
			for command in code:
				if command == '[':
					depth += 1
				if command == ']':
					depth -= 1
				if depth < 0:
					return False
			return depth == 0

		def ensure_size(data, position):
			while not position < len(data):
				data.append(0)

		def get(data, position):
			ensure_size(data, position)
			return data[position]

		def inc(data, position):
			ensure_size(data, position)
			data[position] = min(data[position] + 1, 255)

		def dec(data, position):
			ensure_size(data, position)
			data[position] = max(data[position] - 1, 0)

		if not is_correct_brackets(code):
			raise ValueError('Wrong Bracketing')

		data_pointer = 0
		code_pointer = 0
		data = [0]

		yield [0], data_pointer, code_pointer

		while code_pointer < len(code):
			if code[code_pointer] not in bf.bf_commands:
				code_pointer += 1
				continue

			command = code[code_pointer]

			if command == '+':
				inc(data, data_pointer)
			elif command == '-':
				dec(data, data_pointer)

			if command == '>':
				data_pointer += 1

			if command == '<':
				data_pointer = max(0, data_pointer - 1)

			if command in '+-><':
				code_pointer += 1

			if command == '[':
				if not get(data, data_pointer):
					depth = 1
					while depth:
						code_pointer += 1
						if code[code_pointer] == '[':
							depth += 1
						if code[code_pointer] == ']':
							depth -= 1
				else:
					code_pointer += 1

			if command == ']':
				if get(data, data_pointer):
					while depth:
						code_pointer -= 1
						if code[code_pointer] == '[':
							depth -= 1
						if code[code_pointer] == ']':
							depth += 1
				else:
					code_pointer += 1

			yield data[:], data_pointer, code_pointer

	@staticmethod
	def get_scene(code):

		def tick_data_to_string(ticknumber, before, after):
			from itertools import zip_longest

			bf_array_before_tick, bf_pointer_before_tick, codepos_before_tick = before
			bf_array_after_tick, bf_pointer_after_tick, codepos_after_tick = after

			this_tick = '#range (' + str(ticknumber) + '.0,' + str(ticknumber+1) + '.0)\n'

			this_tick += '#declare intclock = clock-' + str(ticknumber) + '.0;\n'
			this_tick += '#declare code_from = ' + str(codepos_before_tick) + ';\n'
			this_tick += '#declare code_to = ' + str(codepos_after_tick) + ';\n'
			this_tick += '#include "code.pov.inc"\n'

			this_tick += '#declare sl_pos_from = ' + str(bf_pointer_before_tick) + ';\n'
			this_tick += '#declare sl_pos_to = ' + str(bf_pointer_after_tick) + ';\n'
			this_tick += '#include "camandlight.pov.inc"\n';

			for boxpos, (val_before, val_after) in enumerate(zip_longest(bf_array_before_tick, bf_array_after_tick, fillvalue=0)):
				if val_before or val_after:
					this_tick += '#declare boxpos = ' + str(boxpos) + ';\n'
					this_tick += '#declare boxvalue_from = ' + str(val_before) + ';\n'
					this_tick += '#declare boxvalue_to = ' + str(val_after) + ';\n'
					this_tick += '#include "box.pov.inc"\n'
			this_tick += '#break\n'
			return this_tick

		scene_data = bf.get_scene_data(code)
		before, after = next(scene_data), None

		for count, after in enumerate(scene_data):
			yield tick_data_to_string(count, before, after)
			before = after

	@staticmethod
	def get_header():
		scene_amb = '#include "scene_def.pov.inc"\n'
		scene_amb = scene_amb + '#declare code="'+code+'";\n'
		scene_amb = scene_amb + '#switch (clock)\n'
		return scene_amb

	def __init__(self, code, maxticks=200):
		self.code = code
		self.tick_count, self.scene = bf.get_scene(code, maxticks)

def main():
	parser = argparse.ArgumentParser(description='Converts brainfuck code to povray scene')
	parser.add_argument('--fps', metavar='frames_per_second', type=int, default=24)
	parser.add_argument('--fpt', metavar='frames_per_tick', type=int, default=48)
	parser.add_argument('--mt', metavar='maxticks', type=int, default=300)
	parser.add_argument('--width', metavar='width', default='640')
	parser.add_argument('--height', metavar='height', default='480')
	parser.add_argument('--bitrate', metavar='bitrate', default='4000K')
	parser.add_argument('--quiet', action='store_const', const=True)
	#parser.add_argument('--input', metavar='inputfile', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
	parser.add_argument('codefile', metavar='codefile', type=argparse.FileType('r'))
	parser.add_argument('outputfile', metavar='outputfile', type=argparse.FileType('w'))
	args = parser.parse_args()

	code = bf.from_file(args.codefile)
	if not args.quiet:
		print('Brainfuck Code:', code.code)
	tick_count, scene = code.get_scene(code.code, 20)
	print(code.get_full_scene())



def _main():

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
