#!/bin/bash
# Wrapper entrypoint: apply workspace patches, then run original entrypoint.
# Mount this as the container entrypoint to auto-apply patches on every start.

# Apply patches (idempotent, safe to run multiple times)
if [ -f /workspace/.pantheon/patches/apply.py ]; then
    python /workspace/.pantheon/patches/apply.py
fi

# Run original entrypoint
exec /usr/local/bin/docker-entrypoint.sh "$@"
