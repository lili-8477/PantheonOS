#!/bin/bash
# =============================================================================
# Remove a user from PantheonOS Hub
# Usage: ./scripts/remove-user.sh <username> [--purge]
# =============================================================================
set -euo pipefail

HUB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HTPASSWD_FILE="${HUB_DIR}/config/htpasswd"

USERNAME="${1:-}"
PURGE="${2:-}"

if [ -z "$USERNAME" ]; then
    echo "Usage: $0 <username> [--purge]"
    echo ""
    echo "  --purge    Also delete the user's workspace data"
    exit 1
fi

CONTAINER_NAME="pantheon-user-${USERNAME}"
WORKSPACE_DIR="${HUB_DIR}/workspaces/${USERNAME}"

echo "=== Removing user: ${USERNAME} ==="

# ── 1. Stop and remove container ────────────────────────────────────────────
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[1/3] Stopping container..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
    echo "  Removed container ${CONTAINER_NAME}"
else
    echo "[1/3] Container not found (already removed)"
fi

# ── 2. Remove auth credentials ──────────────────────────────────────────────
echo "[2/3] Removing auth credentials..."
if [ -f "${HTPASSWD_FILE}" ]; then
    sed -i "/^${USERNAME}:/d" "${HTPASSWD_FILE}"
    echo "  Removed from htpasswd"
    # Reload nginx to pick up changes
    docker exec pantheon-nginx nginx -s reload 2>/dev/null || true
else
    echo "  No htpasswd file found"
fi

# ── 3. Handle workspace ─────────────────────────────────────────────────────
if [ "$PURGE" = "--purge" ]; then
    echo "[3/3] Purging workspace..."
    if [ -d "${WORKSPACE_DIR}" ]; then
        rm -rf "${WORKSPACE_DIR}"
        echo "  Deleted ${WORKSPACE_DIR}"
    fi
else
    echo "[3/3] Workspace preserved at ${WORKSPACE_DIR}"
    echo "  (use --purge to delete)"
fi

echo ""
echo "=== User '${USERNAME}' removed ==="
