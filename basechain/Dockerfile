# This builds a Docker image that contains hardhat and can be used to
# run a forked EVM network with it.

FROM ghcr.io/foundry-rs/foundry

COPY entrypoint.sh /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
