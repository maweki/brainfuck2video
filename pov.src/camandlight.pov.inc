light_source {
	#declare sl_inbetween_pos = (sl_pos_from - (sl_pos_from - sl_pos_to)*intclock)*1.2;
	<sl_inbetween_pos, 30, 0>
	color White
	spotlight
	radius 0.7
	falloff 1.9
	tightness 10
	point_at <sl_inbetween_pos, 0, 0>
}

camera {
	#declare camfac = (sl_pos_from - (sl_pos_from - sl_pos_to)*intclock*0.8);
	location <1.5+camfac*0.5, 6+camfac*0.3, -5-camfac*0.25>
	look_at  <camfac*0.5, -0.6, 0.6>
	right x*image_width/image_height
}
