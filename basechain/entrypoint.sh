#!/bin/sh

if [ "${FORK_BLOCK_NUMBER}" = "latest" ]
then
  HEIGHT_ARG=""
else
  HEIGHT_ARG="--fork-block-number ${FORK_BLOCK_NUMBER}"
fi

anvil \
  --fork-url "${ENDPOINT}" \
  ${HEIGHT_ARG} \
  --host "0.0.0.0" \
  --no-mining
