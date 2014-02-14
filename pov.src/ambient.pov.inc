background { color Black }

light_source {
	<2, 4, 3>
	color White
	parallel
	point_at <0,0,0>
}

box {
	< -10000, -0.6, -0.6 >, < 10000, 0.6, 0.6 >
	texture {
		pigment {
			color rgb <0.1, 0.1, 0.1>
		}
		finish {
			phong 0.1
			ambient 0.3
			reflection 0.05
		}
	}
}

box {
	< -10000, -1.0, -0.6 >, < 10000, -2.2, -1.8 >
	texture {
		pigment {
			color rgb <0.1, 0.1, 0.1>
		}
		finish {
			phong 0.1
			ambient 0.3
			reflection 0.05
		}
	}
}
