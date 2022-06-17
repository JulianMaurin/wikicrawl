#----------------------------------------------------------------
# MAKEFILE
#----------------------------------------------------------------

# MAKEFLAGS += --silent
UID := $(shell id -u)
GID := $(shell id -g)
DOCKER_COMPOSE ?= docker-compose

.PHONY: help
help:
	@echo "[WIKICRAWL] make help"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help


#----------------------------------------------------------------
# DATABASE
#----------------------------------------------------------------

remove-db:
	$(DOCKER_COMPOSE) down --remove-orphans
	sudo rm -rf ./.databases/neo4j

#----------------------------------------------------------------
# DEV
#----------------------------------------------------------------

CRAWL_RANDOM_PAGE_STUB = "from wikicrawl.core.logging import setup; setup(); from wikicrawl.workers import crawl; crawl('$(shell ls ./.stub/__files | shuf -n 1)')"


crawl-random-stub:  # Push crawling task with random page name from stub 
	$(DOCKER_COMPOSE) run \
		-e LOGGING_ENGINES=STREAM,LOKI \
		-e LOGGING_LEVEL=DEBUG \
		task-queue \
		python -c $(CRAWL_RANDOM_PAGE_STUB)


crawl-random-wikipedia:  ## Push crawling task with random page name using the wikipedia feature "Special:Random"
	$(DOCKER_COMPOSE) run \
		-e LOGGING_ENGINES=STREAM,LOKI \
		task-queue \
		python -c "from wikicrawl.core.logging import setup; setup(); from wikicrawl.workers import crawl; crawl.delay('Special:Random')"


workers-sh:  ## Run workers shell
	$(DOCKER_COMPOSE) run task-queue /bin/ash


buildup:  ## Down + Build + Up
	$(DOCKER_COMPOSE) down --remove-orphans
	$(MAKE) build
	$(DOCKER_COMPOSE) up -d

downup:
	$(DOCKER_COMPOSE) down --remove-orphans
	$(DOCKER_COMPOSE) up -d

#----------------------------------------------------------------
# STUB
#----------------------------------------------------------------

GENERATE_STUB_ENTRYPOINT := Rock
GENERATE_STUB_PAGE_COUNT := 50

generate-stub: build-wheels-dc
	mkdir -p ./.stub/__files ./.stub/mappings
	@echo "Generate stub (entrypoint: $(GENERATE_STUB_ENTRYPOINT), page count: $(GENERATE_STUB_PAGE_COUNT))"
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml down --remove-orphans
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml build \
		--build-arg UID=$(UID) \
		--build-arg GID=$(GID) \
		stub-generator
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml run \
		--user="$(UID):$(GID)" \
		-e LOGGING_ENGINES=STREAM \
		stub-generator \
		python -m wikicrawl.stub generate --entry-point=$(GENERATE_STUB_ENTRYPOINT) --pages-count=$(GENERATE_STUB_PAGE_COUNT)

#----------------------------------------------------------------
# BUILD
#----------------------------------------------------------------

build:  build-wheels-dc ## Build requirements and docker image
	$(DOCKER_COMPOSE) build


build-wheels-dc:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml build \
		--build-arg UID=$(UID) \
		--build-arg GID=$(GID) \
 		build 
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml run \
		--user="$(UID):$(GID)" \
		build \
		make build-wheels

 
build-wheels:  ## To be executed by the docker compose build to generate wheels files (see: build-wheels-dc)
	mkdir -p .build
	$(MAKE) build-wheel PACKAGE=core
	$(MAKE) build-wheel PACKAGE=crawl
	$(MAKE) build-wheel PACKAGE=database
	$(MAKE) build-wheel PACKAGE=workers
	$(MAKE) build-wheel PACKAGE=stub


build-wheel: ## Build wheel for a given package
	(cd ./src/$(PACKAGE); poetry build)
	cp ./src/$(PACKAGE)/dist/*.whl ./.build/

#----------------------------------------------------------------
# Tests
#----------------------------------------------------------------

tests:  ## Run tests using docker compose
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml run \
		--user="$(UID):$(GID)" \
		tests 


tests-sh:  ## Run test container
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml run tests /bin/sh


build-tests-image:  ## Run tests docker image
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml run  \
		--user="$(UID):$(GID)" \
		build \
		make build-requirements
	$(DOCKER_COMPOSE) -f docker-compose.dev.yaml build \
		--build-arg UID=$(UID) \
		--build-arg GID=$(GID) \
		tests

build-requirements:  ## To be executed by the docker compose build to generate requirements files
	mkdir -p .tests/requirements
	$(MAKE) build-requirement PACKAGE=core
	$(MAKE) build-requirement PACKAGE=crawl
	$(MAKE) build-requirement PACKAGE=database
	$(MAKE) build-requirement PACKAGE=workers
	$(MAKE) build-requirement PACKAGE=stub

 
build-requirement: ## Build requirements.txt for a given package
	(cd ./src/$(PACKAGE); poetry export --dev --without-hashes | sed '/^wikicrawl/d' > ./requirements.txt) && mv ./src/$(PACKAGE)/requirements.txt ./.tests/requirements/$(PACKAGE).txt


#----------------------------------------------------------------
# CI
#----------------------------------------------------------------

ci: build-tests-image tests
