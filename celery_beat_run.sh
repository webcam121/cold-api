#!/bin/bash

if [ "$APPLICATION_NAME" == "cold-caller-api-celery-beat-staging" ]
then
    export AGENT_API_SECRET="cold-caller-api-staging"
fi

if [ "$APPLICATION_NAME" == "cold-caller-api-celery-beat-prod" ]
then
    export AGENT_API_SECRET="cold-caller-api-production"
fi

cd /home/ec2-user/cold-caller-api

aws secretsmanager get-secret-value --secret-id $AGENT_API_SECRET --region us-east-2 | jq -r '.SecretString' | jq -r "to_entries|map(\"\(.key)=\\\"\(.value|tostring)\\\"\")|.[]" > .env

docker system prune -f
docker-compose -f docker-compose.celery_beat.yaml stop
docker-compose -f docker-compose.celery_flower.yaml stop
docker-compose -f docker-compose.celery_beat.yaml up -d --build
docker-compose -f docker-compose.celery_flower.yaml up -d --build
