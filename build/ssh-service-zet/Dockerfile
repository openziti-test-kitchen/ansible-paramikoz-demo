ARG TUNNEL_VERSION=latest
FROM docker.io/openziti/ziti-edge-tunnel:$TUNNEL_VERSION
COPY secrets/identities/ssh_server_1.json /ziti-edge-tunnel/ssh_server_1.json
RUN chmod 600 /ziti-edge-tunnel/ssh_server_1.json \
    && chown root:root /ziti-edge-tunnel/ssh_server_1.json
