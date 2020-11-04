#!/bin/bash
BASEDIR=$(dirname "$0")

docker build "$BASEDIR" --tag quay.io/mulbc/data-mover
docker push quay.io/mulbc/data-mover
