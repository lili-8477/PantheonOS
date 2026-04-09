#!/bin/bash
# =============================================================================
# Add a new user to PantheonOS Hub
# Usage: ./scripts/add-user.sh <username> [options]
# =============================================================================
set -euo pipefail

HUB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="${HUB_DIR}/docker-compose.yml"
HTPASSWD_FILE="${HUB_DIR}/config/htpasswd"
SHARED_DATA_DIR="${HUB_DIR}/data/shared"

# ── Parse arguments ──────────────────────────────────────────────────────────
USERNAME=""
API_KEY=""
DATA_MOUNTS=()       # --data /host/path:/container/path or --data /host/path
IMAGE="nanguage/pantheon-agents:latest"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --data|-d)
            shift
            [[ $# -eq 0 ]] && { echo "Error: --data requires a path argument"; exit 1; }
            DATA_MOUNTS+=("$1")
            shift
            ;;
        --image|-i)
            shift
            [[ $# -eq 0 ]] && { echo "Error: --image requires an argument"; exit 1; }
            IMAGE="$1"
            shift
            ;;
        --help|-h)
            cat <<'HELP'
Usage: add-user.sh <username> [api_key] [options]

Options:
  --data, -d PATH       Mount a host directory into the container.
                        Formats:
                          --data /host/path                → mounts to /workspace/data/<dirname>
                          --data /host/path:/container/path → explicit mount point
                        Can be specified multiple times.

  --image, -i IMAGE     Docker image to use (default: nanguage/pantheon-agents:latest)

  --help, -h            Show this help message

Examples:
  add-user.sh alice
  add-user.sh alice sk-ant-api03-xxxxx
  add-user.sh alice --data /home/alice/scrnaseq-data
  add-user.sh alice --data /home/alice/project1:/workspace/projects/project1
  add-user.sh alice --data /data/genome-refs --data /home/alice/my-data
  add-user.sh alice --image pantheon-agents-r:latest --data /home/alice/data
HELP
            exit 0
            ;;
        *)
            # Positional args: username, then api_key
            if [ -z "$USERNAME" ]; then
                USERNAME="$1"
            elif [ -z "$API_KEY" ]; then
                API_KEY="$1"
            else
                echo "Error: Unexpected argument '$1'"
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$USERNAME" ]; then
    echo "Usage: $0 <username> [api_key] [--data /path] [--image image:tag]"
    echo "Run '$0 --help' for full usage."
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

# Build volume mount arguments
VOLUME_ARGS=()
VOLUME_ARGS+=(-v "${WORKSPACE_DIR}:/workspace")

# Shared data directory (read-only, mounted to all users)
if [ -d "$SHARED_DATA_DIR" ]; then
    VOLUME_ARGS+=(-v "${SHARED_DATA_DIR}:/workspace/shared:ro")
    echo "  Mounting shared data: ${SHARED_DATA_DIR} → /workspace/shared (read-only)"
fi

# Per-user data mounts
for mount_spec in "${DATA_MOUNTS[@]+"${DATA_MOUNTS[@]}"}"; do
    if [[ "$mount_spec" == *":"* ]]; then
        # Explicit format: /host/path:/container/path
        host_path="${mount_spec%%:*}"
        container_path="${mount_spec#*:}"
    else
        # Short format: /host/path → /workspace/data/<dirname>
        host_path="$mount_spec"
        dir_name="$(basename "$host_path")"
        container_path="/workspace/data/${dir_name}"
    fi

    # Validate host path exists
    if [ ! -d "$host_path" ]; then
        echo "  Warning: Data path '${host_path}' does not exist, creating it..."
        mkdir -p "$host_path"
    fi

    VOLUME_ARGS+=(-v "${host_path}:${container_path}")
    echo "  Mounting data: ${host_path} → ${container_path}"
done

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
    "${VOLUME_ARGS[@]}" \
    -w /workspace \
    "${IMAGE}"

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
    echo "  Image:      ${IMAGE}"

    # Show mount summary
    if [ ${#DATA_MOUNTS[@]} -gt 0 ] 2>/dev/null; then
        echo "  Data mounts:"
        for mount_spec in "${DATA_MOUNTS[@]}"; do
            if [[ "$mount_spec" == *":"* ]]; then
                echo "    ${mount_spec%%:*} → ${mount_spec#*:}"
            else
                echo "    ${mount_spec} → /workspace/data/$(basename "$mount_spec")"
            fi
        done
    fi
    if [ -d "$SHARED_DATA_DIR" ]; then
        echo "  Shared data: ${SHARED_DATA_DIR} → /workspace/shared (read-only)"
    fi

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
