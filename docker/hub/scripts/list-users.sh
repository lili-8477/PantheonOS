#!/bin/bash
# =============================================================================
# List all PantheonOS Hub users and their status
# =============================================================================
set -euo pipefail

HUB_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== PantheonOS Hub Users ==="
echo ""
printf "%-15s %-12s %-15s %-40s\n" "USERNAME" "STATUS" "CONTAINER" "ID_HASH"
printf "%-15s %-12s %-15s %-40s\n" "--------" "------" "---------" "-------"

# Find all user containers
for container in $(docker ps -a --format '{{.Names}}' | grep '^pantheon-user-' | sort); do
    username="${container#pantheon-user-}"
    status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
    id_hash=$(docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$container" 2>/dev/null | grep '^ID_HASH=' | cut -d= -f2)

    # Color status
    case "$status" in
        running)  status_display="running" ;;
        exited)   status_display="stopped" ;;
        *)        status_display="$status" ;;
    esac

    printf "%-15s %-12s %-15s %-40s\n" "$username" "$status_display" "$container" "${id_hash:-unknown}"
done

echo ""

# Show infrastructure status
echo "=== Infrastructure ==="
for svc in pantheon-nats pantheon-qdrant pantheon-nginx; do
    if docker ps --format '{{.Names}}' | grep -q "^${svc}$"; then
        echo "  ${svc}: running"
    else
        echo "  ${svc}: not running"
    fi
done
