# Pantheon Hub Deployment

Multi-user PantheonOS deployment with shared infrastructure. Each user gets an
isolated container connected via a NATS message broker, sharing a single
Qdrant vector DB. The bundled bioFlow web UI is served by Nginx, and Caddy
provides automatic HTTPS via Let's Encrypt.

## Architecture

```
              Internet
                 │
              ┌──┴──┐  :443 (auto TLS)
              │Caddy│  :80  (HTTP→HTTPS redirect + ACME)
              └──┬──┘
                 │
              ┌──┴──┐  :80  (internal)
              │Nginx│  serves bioFlow UI + proxies /ws/ → NATS
              └──┬──┘
                 │
        ┌────────┼────────┐
        │        │        │
   ┌────┴───┐ ┌──┴──┐ ┌──┴────┐
   │  NATS  │ │ UI  │ │Qdrant │
   │  :4222 │ │(SPA)│ │ :6333 │
   │ WS:8080│ └─────┘ └───┬───┘
   └────┬───┘             │
        │                 │
   ┌────┴───┐ ┌──────┐ ┌──┴───┐
   │ user1  │ │user2 │ │user3 │
   │container│ │  …   │ │  …   │
   └────────┘ └──────┘ └──────┘
```

## Prerequisites

- Docker (with Compose plugin) — `docker compose version` should print v2.x
- A public domain pointed at this host (for HTTPS); skip if running local-only
- Ports 80 and 443 reachable from the internet (port-forward on your router if NAT'd)
- Anthropic / OpenAI / OpenRouter API key(s) for the agents

## Quick Start (Local-Only, HTTP)

For a quick local trial without TLS:

```bash
cd docker/hub

# 1. Comment out the `caddy:` service in docker-compose.yml,
#    and uncomment `ports: ["80:80"]` under nginx (see the comment there).

# 2. Initialize empty config files
mkdir -p config/certs
touch config/htpasswd

# 3. Start shared infrastructure
docker compose up -d

# 4. Add a user (you'll be prompted for a password)
./scripts/add-user.sh alice

# 5. Open http://<server-ip>/ in a browser; copy the Service ID from the
#    add-user.sh output into the UI's Service ID field, and use
#    ws://<server-ip>/ws/ as the NATS URL.
```

## Production Setup (Public HTTPS)

```bash
cd docker/hub

# 1. Configure Caddy with your domain
cp config/Caddyfile.example config/Caddyfile
$EDITOR config/Caddyfile     # replace your-domain.example.com

# 2. Configure shared API keys (optional; per-user .env can override)
cp .env.example .env
$EDITOR .env

# 3. Initialize empty config files
mkdir -p config/certs
touch config/htpasswd

# 4. Start everything (Caddy fetches a Let's Encrypt cert on first request)
docker compose up -d

# 5. Watch cert issuance (look for "certificate obtained successfully")
docker logs -f pantheon-caddy

# 6. Add a user
./scripts/add-user.sh alice

# 7. Open https://<your-domain>/ in a browser. Use the values printed by
#    add-user.sh (NATS URL = wss://<your-domain>/ws/, Service ID = …).
```

## Adding Users

```bash
./scripts/add-user.sh <username> [api_key] [options]

# Examples
./scripts/add-user.sh alice
./scripts/add-user.sh alice sk-ant-api03-xxxxx
./scripts/add-user.sh alice --data /home/alice/scrnaseq-data
./scripts/add-user.sh alice --data /data/refs:/workspace/data/refs
./scripts/add-user.sh alice --image pantheon-agents-r:latest

# By default, user containers run with the pantheon framework code from
# this checkout (../../pantheon/), not the code bundled in the image.
# To use the image's bundled code instead:
./scripts/add-user.sh alice --no-code

# Or point at a different checkout:
./scripts/add-user.sh alice --code /elsewhere/PantheonOS/pantheon
```

Behavior:
- Creates `workspaces/<user>/` (volume-mounted into the container)
- Generates `workspaces/<user>/.env` (per-user API keys override hub `.env`)
- Adds an htpasswd entry for `/nats/` admin auth
- Computes a deterministic 12-char `ID_HASH` from the username
- Starts a `pantheon-user-<user>` container on the hub network
- Prints the URL the user opens in their browser

```bash
./scripts/list-users.sh           # list active user containers
./scripts/remove-user.sh alice    # stop + remove a user
```

## With R Support (Seurat etc.)

```bash
# Build the R-enabled image (one-time)
docker build -t pantheon-agents-r:latest ../r-runtime/

# Persist R packages on a volume so they survive container recreation
docker volume create r-libs

# Install Seurat + ecosystem (one-time, ~30 min)
docker run --rm -v r-libs:/usr/local/lib/R/site-library \
    pantheon-agents-r:latest \
    R -e "install.packages('Seurat', repos='https://cloud.r-project.org', Ncpus=4)"

# Add a user with the R image
./scripts/add-user.sh alice --image pantheon-agents-r:latest
```

R packages live on the `r-libs` volume so they persist across container restarts
and the image stays lean.

## Configuration

### Per-user workspace

Each user gets `workspaces/<user>/` with:
- `.env` — API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, …)
- `.pantheon/` — agents, teams, skills, settings (auto-created on first run)

To customize defaults (model tiering, skill injection, etc.) copy
`settings.json.template` to `workspaces/<user>/.pantheon/settings.json` and edit.

### Hub-wide shared data

Anything placed in `data/shared/` is mounted **read-only** at
`/workspace/shared` in every user container — useful for shared reference
genomes or large datasets.

## Files

```
hub/
├── docker-compose.yml         # All shared services
├── .env.example               # Template for shared API keys
├── config/
│   ├── nginx.conf             # Internal reverse proxy
│   ├── nats-ws.conf           # NATS WebSocket config
│   └── Caddyfile.example      # Template for HTTPS config
├── scripts/
│   ├── add-user.sh
│   ├── remove-user.sh
│   └── list-users.sh
└── settings.json.template     # Per-user workspace settings template
```

## Troubleshooting

**Caddy can't get a cert** — Make sure your domain's A record points to this
host's public IP, and that ports 80 + 443 are reachable from the internet.
ISPs sometimes block these; on Google Wifi / Google Fiber check the Port
Management section. Verify external reachability with `curl -I http://<your-domain>/`
from a phone on cellular.

**`add-user.sh` says "docker network not found"** — You haven't run
`docker compose up -d` yet, or you're running from outside `docker/hub/`.

**UI loads but kernel cells produce no output** — The kernel may have been
restarted (variables are wiped). Use the notebook's "Run All" or restart the
kernel and re-execute from the top.

**`/ws/` returns 400 in `curl`** — Expected; that endpoint requires a WebSocket
upgrade. Test from the browser instead.
