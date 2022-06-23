#!/usr/bin/env bash
set -o nounset
set -x

declare -a REQUIRED_JWTS=(
    "ssh_client_1"
    "ssh_server_1"
    "ssh_server_2"
)

BSRC="$(dirname "${BASH_SOURCE[0]}")"
SECRETS="${BSRC}/secrets"
JWT_DIR="${SECRETS}/tokens"
IDENTITIES_DIR="${SECRETS}/identities"

pushd "$BSRC" &> /dev/null || exit 1

if ! command -v python &> /dev/null; then
    echo "Could not locate python."
    exit 1
fi

if ! python  -c "import openziti" &> /dev/null; then
    echo "Could not import openziti library."
    echo "pip install -r ${BSRC}/requirements.txt"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Could not locate docker-compose."
    exit 1
fi

pushd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null || exit 1

for jwt in "${REQUIRED_JWTS[@]}"; do
    if ! [[ -f "${JWT_DIR}/${jwt}.jwt" ]]; then
        echo "Missing required JWT: ${JWT_DIR}/${jwt}.jwt"
        exit 1
    fi
done

for jwt in "${REQUIRED_JWTS[@]}"; do
    if ! [[ -f "${IDENTITIES_DIR}/${jwt}.json" ]];  then
        echo -n "Enrolling JWT: ${JWT_DIR}/${jwt}.jwt..."
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
