#!/bin/bash
# =============================================================================
# Add a new user to PantheonOS Hub
# Usage: ./scripts/add-user.sh <username> [api_key]
# =============================================================================
set -euo pipefail

HUB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="${HUB_DIR}/docker-compose.yml"
HTPASSWD_FILE="${HUB_DIR}/config/htpasswd"

USERNAME="${1:-}"
API_KEY="${2:-}"

if [ -z "$USERNAME" ]; then
    echo "Usage: $0 <username> [anthropic_api_key]"
    echo ""
    echo "Examples:"
    echo "  $0 alice                          # Will prompt for password, use shared API key"
    echo "  $0 alice sk-ant-api03-xxxxx       # With user's own API key"
    exit 1
fi

# Validate username (alphanumeric + hyphens only)
if ! echo "$USERNAME" | grep -qE '^[a-z0-9][a-z0-9-]*$'; then
    echo "Error: Username must be lowercase alphanumeric (hyphens allowed, can't start with hyphen)"
    exit 1
fi

WORKSPACE_DIR="${HUB_DIR}/workspaces/${USERNAME}"
CONTAINER_NAME="pantheon-user-${USERNAME}"

# Check if user already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Error: User '${USERNAME}' already exists. Remove first with ./scripts/remove-user.sh ${USERNAME}"
    exit 1
fi

echo "=== Adding user: ${USERNAME} ==="

# ── 1. Create workspace ─────────────────────────────────────────────────────
echo "[1/4] Creating workspace..."
mkdir -p "${WORKSPACE_DIR}/.pantheon"

# Create user .env file
if [ ! -f "${WORKSPACE_DIR}/.env" ]; then
    cat > "${WORKSPACE_DIR}/.env" << EOF
# PantheonOS - User: ${USERNAME}
# Add your API keys here. If empty, the system default will be used.
EOF
    if [ -n "$API_KEY" ]; then
        echo "ANTHROPIC_API_KEY=${API_KEY}" >> "${WORKSPACE_DIR}/.env"
    else
        echo "#ANTHROPIC_API_KEY=sk-ant-your-key-here" >> "${WORKSPACE_DIR}/.env"
    fi
    echo "  Created ${WORKSPACE_DIR}/.env"
fi

# ── 2. Add HTTP auth credentials ────────────────────────────────────────────
echo "[2/4] Setting up authentication..."
echo -n "Enter password for ${USERNAME}: "
read -rs PASSWORD
echo ""

if command -v htpasswd &> /dev/null; then
    htpasswd -b "${HTPASSWD_FILE}" "${USERNAME}" "${PASSWORD}"
else
    # Generate via docker if htpasswd not installed locally
    ENTRY=$(docker run --rm httpd:alpine htpasswd -nb "${USERNAME}" "${PASSWORD}")
    # Remove user if already exists, then append
    sed -i "/^${USERNAME}:/d" "${HTPASSWD_FILE}" 2>/dev/null || true
    echo "${ENTRY}" >> "${HTPASSWD_FILE}"
fi
echo "  Added auth credentials"

# Reload nginx if running
docker exec pantheon-nginx nginx -s reload 2>/dev/null || true

# ── 3. Generate unique ID_HASH ──────────────────────────────────────────────
echo "[3/4] Generating unique ID..."
ID_HASH=$(echo -n "pantheon-hub-${USERNAME}" | sha256sum | cut -c1-12)
echo "  ID_HASH: ${ID_HASH}"

# ── 4. Start the container ──────────────────────────────────────────────────
echo "[4/4] Starting Pantheon container..."

# Load shared env if exists
SHARED_ENV_ARGS=""
if [ -f "${HUB_DIR}/.env" ]; then
    SHARED_ENV_ARGS="--env-file ${HUB_DIR}/.env"
fi

docker run -d \
    --name "${CONTAINER_NAME}" \
    --network pantheon-hub_pantheon-network \
    --restart unless-stopped \
    -e PANTHEON_MODE=hub \
    -e "ID_HASH=${ID_HASH}" \
    -e PANTHEON_REMOTE_BACKEND=nats \
    -e NATS_SERVERS=nats://pantheon-nats:4222 \
    -e NATS_MONITOR_URL=http://pantheon-nats:8222 \
    -e QDRANT_LOCATION=http://pantheon-qdrant:6333 \
    -e QDRANT_HTTP_URL=http://pantheon-qdrant:6333 \
    --env-file "${WORKSPACE_DIR}/.env" \
    ${SHARED_ENV_ARGS} \
    -v "${WORKSPACE_DIR}:/workspace" \
    -w /workspace \
    nanguage/pantheon-agents:latest

# Wait for container to start
sleep 3

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "=== User '${USERNAME}' added successfully ==="
    echo ""
    echo "Connection details:"
    echo "  Container:  ${CONTAINER_NAME}"
    echo "  ID_HASH:    ${ID_HASH}"
    echo "  Workspace:  ${WORKSPACE_DIR}"
    echo ""
    echo "To connect via Pantheon UI:"
    echo "  1. Open https://pantheon-ui.aristoteleo.com"
    echo "  2. Set NATS WebSocket URL to: ws://${USERNAME}:<password>@<your-server-ip>:8080"
    echo "  3. Set Service ID to: ${ID_HASH}"
    echo ""
    echo "Or use the full connection URL:"
    echo "  https://pantheon-ui.aristoteleo.com/#/?nats=ws://${USERNAME}:<password>@<your-server-ip>:8080&service=${ID_HASH}&auto=true"
else
    echo "Error: Container failed to start. Check logs:"
    echo "  docker logs ${CONTAINER_NAME}"
    exit 1
fi
