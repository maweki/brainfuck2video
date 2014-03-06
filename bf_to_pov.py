#!/usr/bin/python3

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
	def get_header(code):
		scene_amb = '#version 3.7;\n'
		scene_amb += '#include "scene_def.pov.inc"\n'
		scene_amb += '#declare code="' + code + '";\n'
		scene_amb += '#switch (clock)\n'
		return scene_amb

def main():
	parser = argparse.ArgumentParser(description='Converts brainfuck code to povray scene')
	parser.add_argument('--fps', metavar='frames_per_second', type=int, default=24)
	parser.add_argument('--fpt', metavar='frames_per_tick', type=int, default=48)
	parser.add_argument('--width', metavar='width', default='640')
	parser.add_argument('--height', metavar='height', default='480')
	parser.add_argument('--quiet', action='store_const', const=True)
	parser.add_argument('codefile', metavar='codefile', type=argparse.FileType('r'))
	parser.add_argument('outputfile', metavar='outputfile')
	args = parser.parse_args()

	cleaned_code = bf.clean_text(args.codefile.read())

	if not args.quiet:
		print('Brainfuck Code:', cleaned_code)

	import tempfile
	with tempfile.NamedTemporaryFile(mode='w', suffix='.pov') as scenefile, \
	tempfile.TemporaryDirectory() as scene_output_directory:
		imgprefix = 'scene'
		scenefile.write(bf.get_header(cleaned_code))
		tickcount = None
		for tickcount, frame in enumerate(bf.get_scene(cleaned_code)):
			scenefile.write(frame)
			scenefile.write('\n')
		scenefile.write('#end\n')
		scenefile.flush()
		tickcount += 1
		framecount = tickcount*args.fpt
		image_file_prefix = scene_output_directory + os.sep + imgprefix
		import subprocess
		ret_povray = subprocess.call(['povray',
			'+Lpov.src', # correct include path
			'-V', #quiet
			'+KI0.0', '+KF' + str(tickcount) + '.0', '+KFF' + str(framecount),
			'+Q8', '+A', '-GD', '-GR', '-GS', '-GA',
			'+O' + image_file_prefix,
			'+H' + args.height, '+W' + args.width,
			scenefile.name])
		if ret_povray == 0:
			ret_ffmpeg = subprocess.call(['ffmpeg', '-y',
				'-r', str(args.fps), '-i',
				image_file_prefix + '%0' + str(len(str(framecount))) + 'd.png',
				'-qscale', '0',
				args.outputfile
				])

if __name__ == '__main__':
    main()
