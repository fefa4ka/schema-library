kicad_footprints='https://github.com/KiCad/kicad-footprints' 
kicad_symbols='https://github.com/KiCad/kicad-symbols'

all: build

build: rm
	rm -rf kicad
	git clone $(kicad_footprints) ./kicad/modules
	git clone $(kicad_symbols) ./kicad/library
	make front
	make up
	
front: 
	docker-compose run --rm --entrypoint "yarn install" ui 
	docker-compose run --rm --entrypoint "yarn build" ui

# Proccessing
up:
	docker-compose up -d nginx

stop:
	docker-compose stop --timeout 3

console:
	docker-compose run --rm --entrypoint /bin/sh schema-vc

restart: 
	make front
	make stop
	make up

rebuild:
	docker-compose build schema-vc
	docker-compose run --rm --entrypoint "yarn build" ui

rm:
	make stop
	docker-compose kill schema-vc && docker-compose rm --force schema-vc ui nginx


## docker aliases
ps:
	docker-compose ps
