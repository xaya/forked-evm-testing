#!/usr/bin/env python3

"""
JSON-RPC server that provides some helper / utility functionality for
testing Xaya applications with a forked EVM chain.
"""

import jsonrpclib
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

import json
import os
import time

chainRpc = "http://nginx/chain"
eth = jsonrpclib.ServerProxy (chainRpc)
w3 = Web3 (Web3.HTTPProvider (chainRpc))
w3.middleware_onion.inject (ExtraDataToPOAMiddleware, layer=0)

gsp = jsonrpclib.ServerProxy ("http://nginx/gsp")


def loadAbi (nm):
  with open (os.path.join ("/abi", "%s.json" % nm), "rt") as f:
    data = json.load (f)
  return data["abi"]


erc20abi = loadAbi ("IERC20")

accounts = w3.eth.contract (address=os.getenv ("ACCOUNTS_CONTRACT"),
                            abi=loadAbi ("IXayaAccounts"))
wchi = w3.eth.contract (address=accounts.functions.wchiToken ().call (),
                        abi=erc20abi)

eth.anvil_autoImpersonateAccount (True)


################################################################################


def mineblock ():
  """Mines a block on the EVM chain."""
  eth.evm_mine ()


def mineblockat (timestamp):
  """Mines a block on the EVM chain at the given time."""
  eth.evm_mine (timestamp)


def setbalance (addr, wei):
  """Sets the Ether balance of the given address in Wei."""
  eth.anvil_setBalance (addr, wei)


def ensuregas (addr):
  """
  If the address has less than a minimum balance, increase the balance
  to the minimum to ensure it can pay for gas.
  """

  minBalance = "1"
  minWei = w3.to_wei (minBalance, "ether")

  if w3.eth.get_balance (addr, "latest") < minWei:
    setbalance (addr, minWei)


def transfertoken (token, sender, receiver, amount):
  """
  Transfers the given amount of some ERC20 token from the
  sender to the receiver address, using account impersonation.
  """

  ensuregas (sender)

  c = w3.eth.contract (address=token, abi=erc20abi)
  c.functions.transfer (receiver, amount).transact ({"from": sender})

  mineblock ()


def tryRegisterName (ns, name, receiver):
  """
  If the specified name does not exist, register it for the receiver and
  return True.  Otherwise (the name exists already), returns False.
  """

  if accounts.functions.exists (ns, name).call ():
    return False

  ensuregas (receiver)
  wchi.functions.approve (accounts.address, 2**256-1) \
      .transact ({"from": receiver})
  mineblock ()
  accounts.functions.register (ns, name).transact ({"from": receiver})
  mineblock ()

  return True


def getNameOwner (ns, name):
  """
  For an existing name, retrieve the owner address and return it along
  with the name's token ID.
  """

  tokenId = accounts.functions.tokenIdForName (ns, name).call ()
  owner = accounts.functions.ownerOf (tokenId).call ()

  return owner, tokenId


def getname (ns, name, receiver):
  """
  Gets the specified name into the receiver address.  If the name does not
  exist yet, it will be registered.  If it exists, then it will be transferred
  using address impersonation.
  """

  if tryRegisterName (ns, name, receiver):
    return

  owner, tokenId = getNameOwner (ns, name)

  ensuregas (owner)
  accounts.functions.transferFrom (owner, receiver, tokenId) \
      .transact ({"from": owner})
  mineblock ()


def sendmove (ns, name, mv):
  """
  Sends a move with the given name without transferring it to another
  address.  The owner of the name is impersonated just to send the move
  itself.  If the name does not exist, this method fails.
  """

  if type (mv) != str:
    mv = json.dumps (mv, separators=(",", ":"))

  if not accounts.functions.exists (ns, name).call ():
    raise RuntimeError ("name %s/%s does not exist yet" % (ns, name))

  owner, _ = getNameOwner (ns, name)

  ensuregas (owner)
  accounts.functions.move (ns, name, mv, 2**256-1, 0, "0x" + "00" * 20) \
      .transact ({"from": owner})
  mineblock ()


def syncgsp ():
  """
  Waits for the GSP to be synced up-to-date to the latest block of the
  basechain node.
  """

  blk = w3.eth.get_block ("latest")["hash"].hex ()
  if blk[:2] == "0x":
    blk = blk[2:]
  assert len (blk) == 64

  while True:
    state = gsp.getnullstate ()
    if state["state"] == "up-to-date" and state["blockhash"] == blk:
      break
    time.sleep (0.1)


################################################################################

srv = SimpleJSONRPCServer (('helper', 8000))

srv.register_function (mineblock)
srv.register_function (mineblockat)

srv.register_function (setbalance)
srv.register_function (ensuregas)

srv.register_function (transfertoken)

srv.register_function (getname)
srv.register_function (sendmove)

srv.register_function (syncgsp)

srv.serve_forever ()
