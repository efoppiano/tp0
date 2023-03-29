SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init
TESTING ?= 0
REBUILD ?= 1
RERUN ?= 0

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

docker-compose-up:
	if [ $(REBUILD) -eq 1 ]; then \
		make docker-image; \
	fi

	if [ $(TESTING) -eq 1 ]; then \
		docker compose --profile testing -f docker-compose-dev.yaml up -d --build; \
	else \
		docker compose -f docker-compose-dev.yaml up -d --build; \
	fi
.PHONY: docker-compose-up

docker-compose-up-testing:
	TESTING=1 make docker-compose-up
.PHONY: docker-compose-up-testing

docker-compose-down:
	if [ $(TESTING) -eq 1 ]; then \
		docker compose --profile testing -f docker-compose-dev.yaml stop -t 1; \
		docker compose --profile testing -f docker-compose-dev.yaml down; \
	else \
		docker compose -f docker-compose-dev.yaml stop -t 1; \
		docker compose -f docker-compose-dev.yaml down; \
	fi
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs

test-netcat-auto:
	if [ $(RERUN) -eq 1 ]; then \
		make docker-compose-up-testing; \
	fi
	docker exec netcat sh -c "echo 'Hello World!' | nc server 12345"
	docker exec netcat sh -c "echo 'Elian Foppiano' | nc server 12345"
.PHONY: test-netcat

test-netcat-manual:
	if [ $(RERUN) -eq 1 ]; then \
		make docker-compose-up-testing; \
	fi
	docker exec -ti netcat /bin/sh
.PHONY: test-netcat