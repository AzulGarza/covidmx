IMAGE := covidmx
ROOT := $(shell dirname $(realpath $(firstword ${MAKEFILE_LIST})))
PORT := 8888
JUPYTER_KIND := lab
STORAGE_DIR := storage

DOCKER_PARAMETERS := \
	--user $(shell id -u) \
	-v ${ROOT}:/covidmx \
	-w /covidmx

init:
	docker build . -t ${IMAGE} && mkdir -p ${STORAGE_DIR}

jupyter:
	docker run -d --rm ${DOCKER_PARAMETERS} -e HOME=/tmp -p ${PORT}:8888 ${IMAGE} \
		bash -c "jupyter ${JUPYTER_KIND} --ip=0.0.0.0 --no-browser --NotebookApp.token=''"
