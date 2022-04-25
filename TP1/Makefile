SHELL := /bin/bash
PWD := $(shell pwd)

default: up

docker-image:
	docker build -f ./server/Dockerfile -t "server:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	docker build -f ./informe/Dockerfile -t "informe:latest" .
.PHONY: docker-image

manual:
	@# heavily recommend to use rlwrap for this (`sudo apt install rlwrap`)
	@# (rlwrap allows to use the up and down arrow keys to navigate through the history)
	@if [ "$(shell which rlwrap)" ]; then\
        echo "rlwrap --always-readline docker attach tp1_client_1";\
        echo "Don't forget to press enter to enter interactive mode!";\
		rlwrap --always-readline docker attach tp1_client_1;\
	else\
		echo "docker attach tp1_client_1";\
        echo "Don't forget to press enter to enter interactive mode!";\
		docker attach tp1_client_1;\
    fi
.PHONY: manual

up: docker-image
	docker-compose -f docker-compose-dev.yaml up --detach
.PHONY: up

down:
	docker-compose -f docker-compose-dev.yaml stop --timeout 1
	docker-compose -f docker-compose-dev.yaml down --remove-orphans
.PHONY: down

logs:
	docker-compose -f docker-compose-dev.yaml logs -f
.PHONY: logs

informe:
	docker run --rm -v `pwd`:/data dstockhammer/plantuml -tpng informe/diagrams/*.puml
	docker run --rm -v `pwd`:/pandoc dalibo/pandocker informe/header.yaml README.md --output informe.pdf
.PHONY: informe
