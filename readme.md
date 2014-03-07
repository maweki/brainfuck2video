# Brainfuck to Video
This is a small script that takes a brainfuck code snippet, runs it, saves the
state information for every tick in the brainfuck machine model. From this it
generates a povray script that describes an animation showing the changing
state of the machine.
And these pictures get converted to an actual video via ffmpeg.

## What does it look like
Here is a video generated from a previous version that looks very close to the
current version's output.
* http://www.youtube.com/watch?v=wjogS7SRbow

You can send me links of your generated videos and I'll put them here.

## Usage
	Converts brainfuck code to a povray scene to a video
	
	positional arguments:
	  codefile
	  outputfile

	optional arguments:
	  -h, --help            show this help message and exit
	  --fps frames_per_second
	  --fpt frames_per_tick
	  --width width
	  --height height

## Requirements
* povray (preferably 3.7)
* ffmpeg

## what's missing?
At the moment, input and output (, and .) do not work. I want to fix this
in the near future

## Licence
The project itself is licenced as MIT Licence. The distributed font VeraMono.ttf
is licenced under GPLv2.