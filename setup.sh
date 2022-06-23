#!/usr/bin/env bash
set -o nounset
set -x

declare -a REQUIRED_JWTS=(
    "ssh_client_1"
    "ssh_server_1"
    "ssh_server_2"
)

declare -a DEPENDENCIES=(
    "python"
    "docker-compose"
    "ssh-keygen"
)

BSRC="$(dirname "${BASH_SOURCE[0]}")"
SECRETS="${BSRC}/secrets"
JWT_DIR="${SECRETS}/tokens"
IDENTITIES_DIR="${SECRETS}/identities"
SSH_KEY="${SECRETS}/ssh/ziggy_id_rsa"
SSHD_KEY="${SECRETS}/sshd/host_key_file.key"

pushd "$BSRC" &> /dev/null || exit 1

function generate_key {
    local keyfile="$1"
    if ! ssh-keygen -b 4096 -t rsa -f "${keyfile}" -q -N "" -C ""; then
        echo "Error generating key: ${keyfile}"
        exit 1
    fi
}

for dep in "${DEPENDENCIES[@]}"; do
    if ! command -v "${dep}" &> /dev/null; then
        echo "Could not locate dependency: ${dep}"
        exit 1
    fi
done

if ! python  -c "import openziti" &> /dev/null; then
    echo "Could not import openziti library."
    echo "pip install -r ${BSRC}/requirements.txt"
    exit 1
fi

pushd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null || exit 1

if ! [[ -f "${SSH_KEY}" ]]; then
    echo "Generating SSH key file..."
    generate_key "${SSH_KEY}"
    echo "Done"
fi

if ! [[ -f "${SSHD_KEY}" ]]; then
    echo -n "Generating SSHD key file..."
    generate_key "${SSHD_KEY}"
    rm -f "${SSHD_KEY}.pub"
    echo "Done"
fi


for jwt in "${REQUIRED_JWTS[@]}"; do
    if ! [[ -f "${JWT_DIR}/${jwt}.jwt" ]]; then
        echo "Missing required JWT: ${JWT_DIR}/${jwt}.jwt"
        exit 1
    fi
done

for jwt in "${REQUIRED_JWTS[@]}"; do
    if ! [[ -f "${IDENTITIES_DIR}/${jwt}.json" ]];  then
        echo "Enrolling JWT: ${JWT_DIR}/${jwt}.jwt..."
        if ! python -m openziti enroll \
            --jwt "${JWT_DIR}/${jwt}.jwt" \
            --identity "${IDENTITIES_DIR}/${jwt}.json" &> /dev/null; then
            echo "ERROR"
            exit 1
        fi
        echo "Done"
    fi
done

docker-compose build --parallel --force-rm --no-cache || exit 1
docker-compose up -d || exit 1

popd &> /dev/null || exit 1

echo "Setup Complete!!"
