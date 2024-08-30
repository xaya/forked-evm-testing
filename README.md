# Fork-Network Testing for Xaya

This repository provides a Docker Compose configuration that allows
running a blockchain node forked from Polygon mainnet (or in fact any
other EVM network) for testing Xaya applications.

It also contains a connected Xaya X instance, a custom GSP and a helper JSON-RPC
server that provides some utility methods such as mining blocks on demand with
a desired timestamp.

## Configuration

The desired underlying blockchain to be forked needs to be configured.  For
this, some variables have to be defined in the `.env` file (see `.env.example`):

- `BLOCKCHAIN_ENDPOINT`:  The JSON-RPC endpoint URL for the underlying
  blockchain network that should be forked (e.g. Polygon mainnet).  This needs
  to be an archival node, such as one provided by Alchemy or Infura.

- `FORK_BLOCK_NUMBER`:  This can be set to `"latest"` to fork from the current
  block on the network, or it can be set to some integer value indicating the
  block height from which to fork.  With this, a specific situation can
  be reproduced as needed.

- `ACCOUNTS_CONTRACT`:  This specifies the address of the `XayaAccounts`
  contract that is used to track moves via Xaya X.  The default value specified
  is the official contract on Polygon mainnet.

## Blockchain Node

When run, the configuration exposes the blockchain node for the forked network
on `http://localhost:8100/chain`.  This is based on
[`anvil`](https://book.getfoundry.sh/reference/anvil/) and thus supports
all the specific RPC methods of `anvil` in addition to the standard EVM ones.
It supports both JSON-RPC and WebSocket connections.

## Xaya X

Xaya X is run internally, connected to the forked blockchain node, and exposed
to a GSP running inside the Docker Compose.  It is not exposed publicly
(which would be difficult to do due to having to bind and report its
IP address for ZMQ notifications).
