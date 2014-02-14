#!/bin/sh
cd scene
povray +L.. +Q8 +A +KI0.0 +KF20.0 +O. +KC +KFF120 +H720 +W1280 ../scene.pov
ffmpeg -r 30 -y -b 4000K -i scene%03d.png scene.mp4
