#!/bin/bash

if [[ -z "$1" ]]
then
  echo "Check help: docker_deploy.sh -h"
else
  CURRENT_DIR=$(pwd)
  DOCKER_IMAGE=""
  ENVIRONMENT_VARIABLE_BASH_FILE=""
  while getopts ":hi:c:" opt; do
    case ${opt} in
      h )
        echo "Usage: docker_deploy.sh [-h] [-i DOCKER_IMAGE] [-c ENVIRONMENT_VARIABLE_BASH_FILE]"
        echo "optional arguments:"
        echo "  -h, --help            show this help message and exit"
        echo "  -i DOCKER_IMAGE, --repository_tag DOCKER_IMAGE
                          Docker image name - [REPOSITORY:TAG]"
        echo "  -c ENVIRONMENT_VARIABLE_BASH_FILE, --flask_app_conf ENVIRONMENT_VARIABLE_BASH_FILE
                          Flask app environemt variable bash file, such as 'export API_NAME=hello.app.flask'"
        exit 0
        ;;
      i )
        DOCKER_IMAGE=$OPTARG
        ;;
      c )
        ENVIRONMENT_VARIABLE_BASH_FILE=$OPTARG
        ;;
      \? )
        echo "Invalid Option: -$OPTARG" 1>&2
        exit 1
        ;;
      : )
        echo "Invalid Option: -$OPTARG requires an argument" 1>&2
        exit 1
        ;;
    esac
  done
  shift $((OPTIND -1))
  if [[ -n "$DOCKER_IMAGE" ]] && [[ -n "$ENVIRONMENT_VARIABLE_BASH_FILE" ]]
  then
    kubectl delete services ${DOCKER_IMAGE}
    kubectl delete deployment ${DOCKER_IMAGE}
    rm -f ${DOCKER_IMAGE}.tar
    echo "--- Start building to docker image... ---"
    docker build --rm -t ${DOCKER_IMAGE} .
    docker save ${DOCKER_IMAGE} > ${DOCKER_IMAGE}.tar
    docker rmi -f ${DOCKER_IMAGE}:latest
    docker load < ${DOCKER_IMAGE}.tar
    docker rmi -f "$(docker images -f 'dangling=true' -q)"
    echo "--- Start deploying to docker kubernetes... ---"
    cd ./deployments
    ./generate_kustomization.py -i ${DOCKER_IMAGE} -c ${CURRENT_DIR}/${ENVIRONMENT_VARIABLE_BASH_FILE}
    kubectl kustomize | kubectl apply -f -
    kubectl describe services ${DOCKER_IMAGE}
    rm -f *.yaml
    echo "--- URL: http://localhost:<NodePort>/<endpoints> ---"
  fi
fi
