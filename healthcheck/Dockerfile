# This is a Python-based Docker image that contains custom scripts that
# check via JSON-RPC if certain services (such as basechain+helper or Xaya X
# or the GSP itself) are up.

FROM python:3

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir jsonrpclib-pelix

WORKDIR "/usr/local/bin"
COPY basechain.py xayax.py .

# There is no real entrypoint, as this container is just used with healthcheck
# from docker compose (and does not itself run a specific service).
ENTRYPOINT ["/usr/bin/tail", "-F", "file-does-not-exist"]
