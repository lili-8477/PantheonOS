# Pantheon Hub Deployment

Multi-user Pantheon deployment with shared infrastructure.

## Architecture

```
                    ┌─────────┐
                    │  Nginx  │ :80 (reverse proxy + auth)
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
        ┌─────┴─────┐  ┌┴────┐  ┌──┴───┐
        │ NATS :4222 │  │ UI  │  │Qdrant│
        │   (WS:8080)│  │(CDN)│  │:6333 │
        └─────┬──────┘  └─────┘  └──┬───┘
              │                     │
    ┌─────────┼─────────┐          │
    │         │         │          │
┌───┴───┐ ┌──┴────┐ ┌──┴────┐    │
│ user1 │ │ user2 │ │ user3 │────┘
│  pod  │ │  pod  │ │  pod  │
└───────┘ └───────┘ └───────┘
```

## Quick Start

```bash
# 1. Start shared infrastructure
docker compose up -d nats qdrant nginx

# 2. Create auth credentials
mkdir -p config/certs
touch config/htpasswd

# 3. Add a user
./scripts/add-user.sh alice

# 4. User connects via Pantheon UI
# URL shown after add-user.sh completes
```

## With R Support

```bash
# Build R runtime image (one-time)
docker build -t pantheon-agents-r:latest ../r-runtime/

# Create R package volume (one-time)
docker volume create r-libs

# Install Seurat + ecosystem (one-time)
docker run --rm -v r-libs:/usr/local/lib/R/site-library \
    pantheon-agents-r:latest \
    R -e "install.packages('Seurat', repos='https://cloud.r-project.org', Ncpus=4)"

# Edit add-user.sh to use:
#   - Image: pantheon-agents-r:latest
#   - Volume: -v r-libs:/usr/local/lib/R/site-library
#   - Entrypoint: --entrypoint /workspace/.pantheon/patches/entrypoint-wrapper.sh
```

## Runtime Patches

The entrypoint wrapper at `.pantheon/patches/entrypoint-wrapper.sh` auto-applies patches on container start. Patches add features not yet in the base image:

- `get_token_stats`: UI token usage display
- `include_tools`: Per-agent tool filtering to reduce LLM context cost

## Configuration

Copy `settings.json.template` to your workspace as `.pantheon/settings.json` and customize:

- Model tiers (`high`/`normal`/`low`)
- Skill injection settings
- API keys (via `.env` file, not settings.json)

## Files

```
hub/
├── docker-compose.yml      # Shared infra
├── config/
│   ├── nginx.conf          # Reverse proxy + auth
│   └── nats-ws.conf        # NATS WebSocket config
├── scripts/
│   ├── add-user.sh         # Add user container
│   ├── remove-user.sh      # Remove user container
│   └── list-users.sh       # List active users
└── settings.json.template  # Workspace settings template
```
