kicad_footprints='https://github.com/KiCad/kicad-footprints' 
kicad_symbols='https://github.com/KiCad/kicad-symbols'

all: build

build: 
	git clone $(kicad_footprints) ./kicad/modules
	git clone $(kicad_symbols) ./kicad/library
	

