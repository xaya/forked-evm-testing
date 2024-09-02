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

- `GSP_IMAGE`:  The Docker image that should be used as the internal GSP.
  It will be started with standard arguments; if anything specific is required,
  either the `docker-compose.yml` file needs to be adapted locally, or the
  Docker image should contain all the required things in its entrypoint.

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

## GSP

The GSP is exposed through a reverse proxy on `http://localhost:8100/gsp`.

## Helper Server

The container also runs a JSON-RPC utility server, which provides some
helper methods to interact more easily and directly with the forked blockchain
in ways that will be useful for testing Xaya applications.  This server is
exposed on `http://localhost:8100/helper`.  It provides the following
methods:

- `mineblock ()`: Mines a new block.
- `mineblockat (TIMESTAMP)`: Mines a new block with the given UNIX timestamp.
  The timestamp must be later than the timestamp of the last mined block.
- `setbalance (ADDRESS, WEI)`: Sets the Ether balance of the given address
  to the specified value (in Wei).
- `ensuregas (ADDRESS)`: Ensures that the given address has at least a
  minimum balance to send usual transactions.
- `transfertoken (TOKEN, FROM, TO, AMOUNT)`: Transfers a given amount
  of some ERC-20 token, impersonating the `FROM` account to authorise
  the transfer.
- `getname (NS, NAME, ADDRESS)`: Gets the specified Xaya name into the
  given address.  If the name does not exist, it will be registered (and
  a WCHI balance is required on `ADDRESS`).  If it exists, it will be
  transferred to `ADDRESS` using impersonation of the existing owner.
- `sendmove (NS, NAME, MV)`: Sends a move with the given name without
  transferring it to a new owner.  If the name does not exist yet, this
  results in an error.
