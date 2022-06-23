ARG TUNNEL_VERSION=latest
FROM docker.io/openziti/ziti-edge-tunnel:$TUNNEL_VERSION
COPY --chmod=600 --chown=root:root secrets/identities/ssh_server_1.json /ziti-edge-tunnel/ssh_server_1.json
