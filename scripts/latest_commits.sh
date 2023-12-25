#!/bin/bash

LATEST_TAG=$(git tag --list --sort=creatordate | tail -n 1)
if [[ -z "${LATEST_TAG}" ]]
then
  echo "LATEST_TAG was empty"
  exit 1
fi
COMMIT_COUNT=$(git rev-list ${LATEST_TAG}.. --count)
echo "${COMMIT_COUNT}"

