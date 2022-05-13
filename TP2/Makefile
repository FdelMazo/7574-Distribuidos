export DOCKER_BUILDKIT = 1
KAGGLE_DATASET = pavellexyr/the-reddit-irl-dataset

up: docker-image
	docker-compose -f docker-compose-dev.yaml up --detach
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
	docker build -f ./server/Dockerfile -t "server:latest" . 
	docker build -f ./feeder/Dockerfile -t "feeder:latest" .
.PHONY: docker-image

logs:
	docker-compose -f docker-compose-dev.yaml logs -f
.PHONY: logs

informe:
	docker run --rm -v `pwd`:/data dstockhammer/plantuml -tpng informe/diagrams/*.puml
	docker run --rm -v `pwd`:/pandoc dalibo/pandocker informe/header.yaml README.md --output informe.pdf
.PHONY: informe
