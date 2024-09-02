#!/usr/bin/env python3

"""
Testing script that runs some commands against the helper JSON-RPC
server and checks that some of the functions work as expected.  This
assumes that the Docker Compose is up and running with a forked Polygon
mainnet chain on localhost:8100.
"""

import jsonrpclib

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

import json
import os
import sys

chainRpc = "http://localhost:8100/chain"
eth = jsonrpclib.ServerProxy (chainRpc)
w3 = Web3 (Web3.HTTPProvider (chainRpc))
w3.middleware_onion.inject (ExtraDataToPOAMiddleware, layer=0)

helper = jsonrpclib.ServerProxy ("http://localhost:8100/helper")

def loadAbi (nm):
  base = os.path.abspath (os.path.dirname (__file__))
  with open (os.path.join (base, "abi", "%s.json" % nm), "rt") as f:
    data = json.load (f)
  return data["abi"]

erc20abi = loadAbi ("IERC20Metadata")

accountsAddr = os.getenv ("ACCOUNTS_CONTRACT")
if accountsAddr is None:
  sys.exit ("ACCOUNTS_CONTRACT is not set")
accounts = w3.eth.contract (address=os.getenv ("ACCOUNTS_CONTRACT"),
                            abi=loadAbi ("IXayaAccounts"))

# Generate a fresh, random address used in the test.  This will only be
# used on the forked local chain.
acc = w3.eth.account.create ()
addr = acc.address
print ("Using test address: %s" % addr)

################################################################################
# Tests for modifying Ether balance and gas.

assert w3.eth.get_balance (addr, "latest") == 0
helper.setbalance (addr, 1234)
assert w3.eth.get_balance (addr, "latest") == 1234
helper.ensuregas (addr)
assert w3.eth.get_balance (addr, "latest") > w3.to_wei ("0.01", "ether")
helper.setbalance (addr, w3.to_wei ("10", "ether"))
helper.ensuregas (addr)
assert w3.eth.get_balance (addr, "latest") == w3.to_wei ("10", "ether")

################################################################################
# Tests for transferring ERC-20 tokens.

usdcAddress = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
usdc = w3.eth.contract (address=usdcAddress, abi=erc20abi)
# A large holder address of USDC on Polygon, from which we can transfer
# tokens using impersonation.  The address here is Aave.
usdcHolder = "0xA4D94019934D8333Ef880ABFFbF2FDd611C762BD"

assert usdc.functions.balanceOf (addr).call () == 0
helper.transfertoken (usdcAddress, usdcHolder, addr, 12345)
assert usdc.functions.balanceOf (addr).call () == 12345
helper.transfertoken (usdcAddress, usdcHolder, addr, 1)
assert usdc.functions.balanceOf (addr).call () == 12346

# We need WCHI anyway later for testing name registration.
wchiAddress = "0xE79feAAA457ad7899357E8E2065a3267aC9eE601"
wchi = w3.eth.contract (address=wchiAddress, abi=erc20abi)
# A large holder, which is the Uniswap pool in this case.
wchiHolder = "0x564D4E21E2B140F746d8004173F23bc8457edaf1"

assert wchi.functions.balanceOf (addr).call () == 0
helper.transfertoken (wchiAddress, wchiHolder, addr, 100_0000_0000)
assert wchi.functions.balanceOf (addr).call () == 100_0000_0000

################################################################################
# Tests with Xaya names.

def ownerOfName (ns, name):
  tokenId = accounts.functions.tokenIdForName (ns, name).call ()
  if not accounts.functions.exists (tokenId).call ():
    return None
  return accounts.functions.ownerOf (tokenId).call ()

# Our address is randomly generated as a hash, so it is unlikely
# to be existing already as Xaya name.
testName = addr
assert ownerOfName ("p", testName) is None
helper.getname ("p", testName, addr)
assert ownerOfName ("p", testName) == addr

# We assume p/domob exists, and use that to "steal" and existing name
# in the test.
oldOwner = ownerOfName ("p", "domob")
assert oldOwner is not None
assert oldOwner != addr
helper.getname ("p", "domob", addr)
assert ownerOfName ("p", "domob") == addr
helper.getname ("p", "domob", oldOwner)

# Sending of moves without taking ownership of a name.
assert ownerOfName ("g", testName) is None
try:
  helper.sendmove ("g", testName, "{}")
  raise AssertionError ("expected error not raised")
except:
  pass
tokenId = accounts.functions.tokenIdForName ("p", "domob").call ()
oldNonce = accounts.functions.nextNonce (tokenId).call ()
helper.sendmove ("p", "domob", "{}")
assert ownerOfName ("p", "domob") == oldOwner
newNonce = accounts.functions.nextNonce (tokenId).call ()
assert newNonce == oldNonce + 1
