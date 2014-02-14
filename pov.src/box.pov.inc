box {
	#if (boxvalue_from = boxvalue_to)
		< boxpos*1.2 - 0.5, 0.5, 0.5>, < boxpos*1.2 + 0.5, 0.6 + (boxvalue_from-0.5) / 100 , -0.5>
	#else
		< boxpos*1.2 - 0.5, 0.5, 0.5>, < boxpos*1.2 + 0.5, 0.6 + (boxvalue_from-0.5 - (boxvalue_from-boxvalue_to)*intclock) / 100 , -0.5>
	#end
	texture {
		pigment {
			color White
		}
		finish {
			phong 0.5
			metallic
		}
	}
}

#if (boxvalue_from = boxvalue_to)
text {
    ttf "VeraMono.ttf" str(boxvalue_from,-3,0) 0.7, 0
    pigment { Red }
    rotate < 90, 0, 0 >
    scale < 0.5, 0.5, 0.5 >
    translate < (1.2*boxpos)-0.4, boxvalue_from/100 + 0.65, -0.2>
}
#else
#if (boxvalue_from != 0)
text {
    ttf "VeraMono.ttf" str(boxvalue_from,-3,0) 0.7, 0
    pigment { Red }
    rotate < 90, 0, 0 >
    scale < 0.5, 0.5, 0.5 >
    translate < (1.2*boxpos)-0.4, boxvalue_from/100 + 0.65-intclock*0.12, -0.2>
}
#end
#if (boxvalue_to != 0)
text {
    ttf "VeraMono.ttf" str(boxvalue_to,-3,0) 0.7, 0
    pigment { Red }
    rotate < 90, 0, 0 >
    scale < 0.5, 0.5, 0.5 >
    translate < (1.2*boxpos)-0.4, boxvalue_to/100 + 0.55+intclock*0.1, -0.2>
}
#end
#end
