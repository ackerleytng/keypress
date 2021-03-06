#!/bin/sh

# Starts gatekeeper up, also configures this client at keycloak
# Pass client roles that you want to add as arguments
# Example: ./start.sh list detail

LOUKETO_VERSION=1.0.0

command -v curl || apt update && apt install curl -y
command -v jq || curl -o /bin/jq -L https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && chmod +x /bin/jq
command -v wait-for-it.sh || curl -o /bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x /bin/wait-for-it.sh

# Setup gatekeeper
[ -f /opt/keycloak-gatekeeper ] || curl -fsSL "https://github.com/louketo/louketo-proxy/releases/download/${LOUKETO_VERSION}/louketo-proxy_${LOUKETO_VERSION}_linux_amd64.tar.gz" | tar -xz --strip-components=1 -C /tmp && chmod +x /tmp/louketo-proxy

curl -sSkL https://caddy.localhost/root.crt -o /usr/local/share/ca-certificates/caddy.crt

# Add caddy root cert in container
update-ca-certificates

# Wait for keycloak to be ready (use a direct connection to the container to
#   test, because traefik (keycloak.localhost) comes up way before the service
#   is ready
wait-for-it.sh -t 60 keycloak:8443

# Sets up this client with keycloak
#   client roles will be passed to setup.sh
client_secret=$(/gatekeeper/setup.sh $@)

echo ">>> Using client_secret=|$client_secret|"
exec /tmp/louketo-proxy --config /tmp/config.yml --client-secret="$client_secret"
