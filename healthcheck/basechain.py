#!/usr/bin/env python3

"""
Basic Python script that checks (via JSON-RPC) if the basechain
JSON-RPC interface can be accessed already.  It does so through nginx,
so in a way is a health check for both of them together.
"""

import jsonrpclib

import sys

srv = jsonrpclib.ServerProxy("http://nginx/chain")
try:
  srv.eth_chainId ()
except:
  sys.exit (-1)
