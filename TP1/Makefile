SHELL := /bin/bash
PWD := $(shell pwd)

default: up

docker-image:
	docker build -f ./server/Dockerfile -t "server:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
.PHONY: docker-image

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
