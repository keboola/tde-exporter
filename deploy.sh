#!/bin/bash
set -e

docker pull quay.io/keboola/developer-portal-cli-v2:latest
export REPOSITORY=`docker run --rm -e KBC_DEVELOPERPORTAL_USERNAME=$KBC_DEVELOPERPORTAL_USERNAME -e KBC_DEVELOPERPORTAL_PASSWORD=$KBC_DEVELOPERPORTAL_PASSWORD quay.io/keboola/developer-portal-cli-v2:latest ecr:get-repository keboola tde-exporter`
docker tag keboola/tde-exporter:latest $REPOSITORY:$TRAVIS_TAG
docker tag keboola/tde-exporter:latest $REPOSITORY:latest
eval $(docker run --rm -e KBC_DEVELOPERPORTAL_USERNAME=$KBC_DEVELOPERPORTAL_USERNAME -e KBC_DEVELOPERPORTAL_PASSWORD=$KBC_DEVELOPERPORTAL_PASSWORD quay.io/keboola/developer-portal-cli-v2:latest ecr:get-login keboola tde-exporter)
docker push $REPOSITORY:$TRAVIS_TAG
docker push $REPOSITORY:latest

## update app in Developer Portal
#docker run --rm -e KBC_DEVELOPERPORTAL_USERNAME=$KBC_DEVELOPERPORTAL_USERNAME -e KBC_DEVELOPERPORTAL_PASSWORD=$KBC_DEVELOPERPORTAL_PASSWORD quay.io/keboola/developer-portal-cli-v2:latest update-app-repository keboola tde-exporter $TRAVIS_TAG
