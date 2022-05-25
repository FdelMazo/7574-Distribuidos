# Considering our data dir might be really big, sending the whole build context on
# docker-build is a bad idea.
# Using Docker's build kit we see a nice performance improvement.
export DOCKER_BUILDKIT = 1

# Just an alias
run: down up logs

up: docker-image
	docker-compose -f docker-compose-dev.yaml --profile query up --detach
	docker-compose -f docker-compose-dev.yaml --profile graph up --detach
	docker-compose -f docker-compose-dev.yaml --profile feeder up --detach
.PHONY: up

down:
	docker-compose -f docker-compose-dev.yaml stop --timeout 1
	docker-compose -f docker-compose-dev.yaml down --remove-orphans
.PHONY: down

docker-image:
	docker build -f ./feeder/Dockerfile -t "feeder:latest" .
	docker build -f ./node/Dockerfile -t "node:latest" .
	docker build -f ./server/Dockerfile -t "server:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
.PHONY: docker-image

logs:
	docker-compose -f docker-compose-dev.yaml logs -f
.PHONY: logs

informe:
	docker run --rm -v `pwd`:/data dstockhammer/plantuml -tpng informe/diagrams/*.puml
	docker run --rm -v `pwd`:/pandoc dalibo/pandocker informe/header.yaml README.md --output informe.pdf
.PHONY: informe
