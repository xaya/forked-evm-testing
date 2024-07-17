# Fork-Network Testing for Xaya

This repository provides a Docker Compose configuration that allows
running a blockchain node forked from Polygon mainnet (or in fact any
other EVM network) for testing Xaya applications.

It also contains a connected Xaya X instance and a custom JSON-RPC server
that provides some utility methods such as mining blocks on demand with
a desired timestamp.

## Configuration

The desired underlying blockchain to be forked needs to be configured.  For
this, two variables have to be defined in the `.env` file (see `.env.example`):

- `BLOCKCHAIN_ENDPOINT`:  The JSON-RPC endpoint URL for the underlying
  blockchain network that should be forked (e.g. Polygon mainnet).  This needs
  to be an archival node, such as one provided by Alchemy or Infura.

- `FORK_BLOCK_NUMBER`:  This can be set to `"latest"` to fork from the current
  block on the network, or it can be set to some integer value indicating the
  block height from which to fork.  With this, a specific situation can
  be reproduced as needed.

## Blockchain Node

When run, the configuration exposes the blockchain node for the forked network
on `http://localhost:8100/chain`.  This is based on
[`anvil`](https://book.getfoundry.sh/reference/anvil/) and thus supports
all the specific RPC methods of `anvil` in addition to the standard EVM ones.
