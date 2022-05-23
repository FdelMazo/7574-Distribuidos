# Considering our data dir might be really big, sending the whole build context on
# docker-build might be a bad idea.
# Using Docker's build kit we see a nice performance improvement.
export DOCKER_BUILDKIT = 1
KAGGLE_DATASET = pavellexyr/the-reddit-irl-dataset

run: down up logs

up: docker-image
	docker-compose -f docker-compose-dev.yaml --profile graph up --detach
	docker-compose -f docker-compose-dev.yaml --profile query up --detach
	docker-compose -f docker-compose-dev.yaml --profile feeder up --detach
.PHONY: up

down:
	docker-compose -f docker-compose-dev.yaml stop --timeout 1
	docker-compose -f docker-compose-dev.yaml down --remove-orphans
.PHONY: down

get-data:
	test -n "$(KAGGLE_USERNAME)"  # Don't forget to set up KAGGLE_USERNAME
	test -n "$(KAGGLE_KEY)"  # Don't forget to set up KAGGLE_KEY
	test -n "$(shell which kaggle)"  # Don't forget to pip install kaggle
	kaggle datasets download $(KAGGLE_DATASET) -f dataset.zip
	unzip dataset.zip -d data
	rm dataset.zip
.PHONY: get-data

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
