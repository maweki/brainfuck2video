#declare codefocus = difference {	
	box {
		< -0.05, 0.5, -0.5 >, < 0.55, -0.5, -0.65 >
		
	}
	box {
		< 0, 0.45, -0.5 >, < 0.5, -0.45, -0.7 >
		
	}
	
	box {
		< -1, 0.4, -0.5 >, < 1, -0.4, -0.7 >
		
	}
	
	
	texture {
		pigment { Green }
		#if (intclock < 0.5)
			#declare amb = -0.6*(intclock*4 - 1)*(intclock*4 - 1)+0.8;
			finish {ambient amb diffuse .6}
		#else
			finish {ambient .2 diffuse .6}
		#end
	}
}

light_source {
<0, 0, 0>
color White

looks_like { codefocus }
}

light_source {
<0.25, 0, -1.0>
color White
}

text {
    #declare text_fac=0.600;
    ttf "VeraMono.ttf" code 0.4, 0
    pigment { Red }
    #if (intclock < 0.5)
    translate < -(code_from)*text_fac, -0.3, -0.7 >
    #else
    translate < -(code_from - (code_from-code_to)*(intclock-0.5)*2)*text_fac
    	, -0.3, -0.7 >
    #end
    
}
