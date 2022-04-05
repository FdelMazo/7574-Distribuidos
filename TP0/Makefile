SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init
CLIENTS=1

default: build

all:

deps:
	go mod tidy
	go mod vendor

build: deps
	GOOS=linux go build -o bin/client github.com/7574-sistemas-distribuidos/docker-compose-init/client
.PHONY: build

docker-image:
	docker build -f ./server/Dockerfile -t "server:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

docker-compose-up: docker-image
	# Ejemplo: corriendo `make CLIENTS=5 docker-compose-up` se crean 5 clientes!
	@#
	@# Qué esta pasando acá? Usando los anchors de yaml vimos que, con solo 4 lineas podemos definir un cliente nuevo:
	@# ```
	@# clientX:
	@#   <<: *client
	@#   container_name: clientX // incluso esta la podríamos ahorrar pero ya fue...
	@#   environment:
	@#     - CLI_ID=X
	@# ```
	@# Entonces, primero buscamos un ancla en nuestro archivo: el triple ### donde vamos a appendear cosas
	@# Después, appendeamos N veces esas 4 lineas
	@# Después pulimos ese string enorme, reemplazando tabs, espacios y newlines (porque yaml es molesto y la indentación es parte de la especificación...)
	@# Y finalmente le pasamos el choclo enorme que acabamos de hacer, por stdin, a docker-compose up
	@# Es trucho, feo, malo, y con jinja o cualquier manera de hacer templates salía mas prolijo, pero funciona!

	@for ((i=2; i<=$(CLIENTS); i++)) ; do      \
        CLIENTSTR=$$CLIENTSTR"\tclient$$i:\n \
		\t\t<<: *client\n \
		\t\tcontainer_name: client$$i\n \
		\t\tenvironment:\n \
		\t\t\t- CLI_ID=$$i\n\n" ; done && \
    sed '/###/r'<(echo -e $$CLIENTSTR | sed 's/\t/  /g') docker-compose-dev.yaml | docker-compose -f - up -d --build

.PHONY: docker-compose-up

docker-compose-server-test:
	docker build -f ./nc-test/Dockerfile -t "nc-test:latest" .
	docker-compose -f docker-compose-dev.yaml run nc-test -d --build
.PHONY: docker-compose-server-test

docker-compose-down:
	docker-compose -f docker-compose-dev.yaml stop -t 1
	# por qué --remove-orphans?
	# porque si vamos a agregar clientes "en runtime"... entonces a la hora de tirarlos abajo no vamos a tener manera de saber a quienes matar!
	docker-compose -f docker-compose-dev.yaml down --remove-orphans
.PHONY: docker-compose-down

docker-compose-logs:
	docker-compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs
