# Builds an image based on the standard nginx but with our custom configuration,
# which runs a reverse proxy for the forked blockchain node and our
# utilities RPC server.

FROM nginx:stable-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY proxy.conf /etc/nginx/conf.d/
