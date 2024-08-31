#!/usr/bin/env python3

"""
Basic Python script that checks (via JSON-RPC) if the Xaya X
JSON-RPC interface can be accessed already.
"""

import jsonrpclib

import sys

srv = jsonrpclib.ServerProxy("http://xayax:8000")
try:
  srv.getnetworkinfo ()
except:
  sys.exit (-1)
