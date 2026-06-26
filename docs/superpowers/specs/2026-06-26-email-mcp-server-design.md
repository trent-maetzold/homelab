# Email MCP Server — Design Spec

**Date:** 2026-06-26  
**Status:** Draft — awaiting implementation planning  
**Stack:** `stacks/mcp-email/`

## Purpose

A containerized MCP server that gives an LLM agent the tools to manage a user’s email with minimal human intervention. The first supported provider is **ProtonMail** via the Proton IMAP/SMTP Bridge. Future providers (Gmail, generic IMAP) must fit the same tool contract.

## Goals

- Run the Proton Bridge and the MCP server in a single container.
- Authenticate configured Proton accounts at runtime with no manual `docker run` step.
- Expose a provider-agnostic set of MCP tools for inbox-zero workflows.
- Keep the project code inside `stacks/mcp-email/` so it can be iterated quickly before moving to its own repo.

## Non-Goals

- Sending email in the MVP (the agent drafts; the user sends from Proton).
- Permanent message deletion (`delete`); only `trash`.
- Generic SMTP/IMAP providers other than Proton in the MVP.
- A GUI, web UI, or admin interface.

## Architecture

One container runs two things:

1. **Proton Mail Bridge** — started in gRPC mode (`proton-bridge --grpc`).
2. **MCP Server** — a FastMCP HTTP/SSE server that uses the `clients` package to talk to each account’s mail backend.

The bridge only accepts local connections, so for ProtonMail the `ProtonMailClient` connects to `127.0.0.1` inside the same container. The MCP server exposes SSE on `0.0.0.0:8000`; Traefik on the `proxy` network routes external clients to it.

### Startup sequence

1. Load `accounts.yaml` and validate with Pydantic.
2. Initialize `pass` / GPG if `/root/.password-store` is missing.
3. Start `proton-bridge --grpc`.
4. Wait for the bridge gRPC config file (`grpcServerConfig.json`).
5. For each configured Proton account:
   - Check if already connected via `GetUserList`.
   - If not, call `Login` (and `Login2FA` / `Login2Passwords` if required).
   - Cache the bridge-generated IMAP/SMTP password from the gRPC `User` response.
6. Start FastMCP on `0.0.0.0:8000`.

### Container layout

```text
stacks/mcp-email/
├── compose.yaml
├── compose.override.yaml
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── README.md
├── config/
│   └── accounts.yaml.example
└── src/
    └── mcp_email/
        ├── clients/
        │   ├── __init__.py
        │   ├── email.py
        │   ├── imap.py
        │   └── protonmail.py
        ├── config.py
        ├── bridge_manager.py
        ├── models.py
        ├── server.py
        ├── __init__.py
        ├── __main__.py
        └── proto/
            └── bridge.proto
```

- `/root` — persisted bridge vault, GPG key, and pass store.
- `/app/config` — mounted `accounts.yaml`.

## Configuration

Primary configuration is a YAML file mounted at `/app/config/accounts.yaml`. Secrets are pulled from env vars referenced by name so the config file can be tracked in git.

```yaml
accounts:
  - name: personal
    provider: proton
    address: me@proton.me
    password_env: PROTON_PERSONAL_PASSWORD
    # Provide one of the following if 2FA is enabled:
    totp_secret_env: PROTON_PERSONAL_TOTP_SECRET  # generates TOTP codes at login
    totp_code_env: PROTON_PERSONAL_TOTP_CODE      # one-time code used at login
```

Pydantic Settings provides optional env overrides (e.g., `MCP_EMAIL_LOG_LEVEL`).

### Config rules

- `name` defaults to `address` if omitted.
- `provider` must be `proton` for the MVP.
- The env var named by `password_env` is required at runtime.
- If Proton 2FA is enabled and neither `totp_secret_env` nor `totp_code_env` is supplied, login fails with a clear error.

## Components

### `config.py`

Loads and validates `accounts.yaml` plus Pydantic Settings env overrides. Exposes a typed `Settings` object to the rest of the app.

### `bridge_manager.py`

Manages the bridge subprocess and a gRPC client generated from `bridge.proto`.

Responsibilities:

- Initialize GPG / `pass` if needed.
- Start / stop `proton-bridge --grpc`.
- Wait for the gRPC socket config.
- Log in configured accounts and handle TOTP/mailbox-password flows.
- Expose per-account state and bridge-generated IMAP/SMTP credentials.

### `clients` package

Provider-agnostic mail clients.

```text
clients.email.EmailClient (abstract)
    └─ clients.imap.ImapClient
           └─ clients.protonmail.ProtonMailClient
```

`clients.email.EmailClient` defines the tool-facing contract:

- `list_folders()`
- `search_emails(folder, ...)`
- `read_email(message_id, mark_read)`
- `mark_email(message_id, read, flagged)`
- `tag_email(message_id, label, action)`
- `move_email(message_id, folder)`
- `trash_email(message_id)`
- `archive_email(message_id)`
- `draft_email(...)`
- `get_summary()`

`clients.imap.ImapClient` implements the contract using `imapclient` + STARTTLS. It is generic and can target any IMAP/SMTP host and port; only `ProtonMailClient` defaults to the local bridge. It exposes small provider hooks that subclasses override:

- `trash_folder_name()`
- `archive_folder_name()`
- `drafts_folder_name()`
- `sent_folder_name()`
- `inbox_folder_name()`
- `normalize_label(label)`
- `archive_message(conn, message_id)` — default moves to archive folder.

`clients.protonmail.ProtonMailClient` only overrides Proton folder/label semantics (e.g., archive moves to the `Archive` folder, labels are copied/deleted in label folders). No generic IMAP code lives in the Proton class.

### `server.py`

FastMCP server. Registers one tool per `EmailClient` method. Mounts:

### `models.py`

Pydantic models:

- `AccountConfig`
- `Folder`
- `EmailSummary`
- `Email`
- `Draft`

## Tool Contract

All tools accept a `mailbox` argument that matches a configured account `name` (defaulting to the account address).

| Tool | Args | Description |
|------|------|-------------|
| `list_mailboxes` | — | Configured accounts + connection status + unread count. |
| `list_folders` | `mailbox` | List folders/labels for the account. |
| `search_emails` | `mailbox`, `folder`, `subject`, `from_address`, `since`, `unread_only`, `limit`, `offset` | Search and return email summaries. |
| `read_email` | `mailbox`, `message_id`, `mark_read=true` | Return full email body + attachment metadata. |
| `mark_email` | `mailbox`, `message_id`, `read`, `flagged` | Set/clear `\\Seen` or `\\Flagged`. |
| `tag_email` | `mailbox`, `message_id`, `label`, `action="add"` | Add or remove a label. |
| `move_email` | `mailbox`, `message_id`, `folder` | Move to an arbitrary folder. |
| `trash_email` | `mailbox`, `message_id` | Move to Trash. |
| `archive_email` | `mailbox`, `message_id` | Archive the message. |
| `draft_email` | `mailbox`, `to`, `subject`, `body`, `html_body`, `cc`, `bcc`, `reply_to_message_id` | Append a draft to Drafts. `html_body` is optional; when present the draft is multipart alternative.

All tool inputs and outputs are primitives or Pydantic models — never bare `dict`s.

### Stable identifiers

Tools expose the `Message-ID` header as `message_id`. Internally the client maps `Message-ID` to IMAP UID per folder/request. This keeps IDs stable across moves and provider-specific UID schemes.

## Data Flow Examples

1. FastMCP receives `read_email(mailbox="personal", message_id="<abc@example.com>")`.
2. `server.py` asks `bridge_manager` for the bridge password for `personal`.
3. The server instantiates a `clients.protonmail.ProtonMailClient` for that account, connected to the local bridge at `127.0.0.1:1143`.
4. Select the requested folder and search `HEADER Message-ID <abc@example.com>`.
5. Fetch `text/plain`, `text/html`, and `BODYSTRUCTURE` for attachments.
6. If `mark_read=True`, set `\\Seen`.
7. Return an `Email` model.

### Draft a reply

1. FastMCP receives `draft_email(..., reply_to_message_id="<orig@example.com>")`.
2. Read the original message to obtain `Message-ID`, `From`, and `Subject`.
3. Build a new RFC 2822 message with `In-Reply-To` and `References` headers.
4. `APPEND` the message to the Drafts folder.
5. Return the new draft’s `message_id`.

## Error Handling

- **Config errors:** fail fast on startup; container exits with a clear message.
- **Bridge login failures:** per-account. The server still starts; tools for a failed account return an MCP error describing the failure.
- **IMAP errors:** caught and returned as tool errors; no raw stack traces leak to the client.
- **Health check:** `/health` returns 200 once the MCP HTTP server is listening. It intentionally does **not** gate on bridge sync state.

## Security

- Proton credentials live only in env vars / Docker secrets, never in tracked config.
- The bridge vault and GPG key live in a persisted Docker volume.
- gRPC communication with the bridge is local-only over TLS; the token is read from the bridge-written config file.
- IMAP/SMTP connections use STARTTLS. For ProtonMail they go to the local bridge; the generic `ImapClient` can target any host/port.
- No authentication is implemented on the MCP SSE endpoint in the MVP; it is assumed to be behind Traefik/Authelia.

## Testing

- Unit tests for `config.py` loading and validation.
- Unit tests for `models.py`.
- Fake IMAP server tests for `ImapClient` search/move/tag logic.
- Manual smoke test script against a real Proton account.

## Deployment

### Base image

Use `ghcr.io/trent-maetzold/protonmail-bridge:build` pinned to a specific digest as the base. It already contains the headless bridge binary, `pass`, `socat`, and GPG params. The Dockerfile adds Python 3.12, `uv`, and the `mcp_email` package.

### Compose outline

- Service `server` with `container_name: mcp_email`.
- `restart: unless-stopped`.
- Volume mounts:
  - `/mnt/cache/appdata/mcp_email/server/bridge:/root`
  - `/mnt/cache/appdata/mcp_email/server/config:/app/config:ro`
- Network: `proxy` (external) for Traefik.
- Environment: `TZ`, `MCP_EMAIL_LOG_LEVEL`, and the per-account secret env vars.
- Traefik labels for `mcp-email.trkm.io` (or chosen host).
- Healthcheck hitting `/health`.

### `compose.override.yaml`

Unraid composeman labels only: managed, icon, webui, shell.

## Future Work
- A future `GmailClient` subclass and OAuth-based account config.
- A `send_email` / `send_draft` tool once the user wants full agent sending.
- Support for multiple IMAP/SMTP ports or remote bridge hosts.
- Configurable folder namespaces per account.

## Decisions Made

- Draft-only, no send, in MVP.
- HTTP/SSE transport, listening on `0.0.0.0`, exposed through Traefik.
- Account configuration via YAML file; secrets via referenced env vars.
- Bridge authenticated at runtime automatically using gRPC.
- Trash only; no permanent delete.
- `tag_email` operates on Proton labels.
- Provider-agnostic tool contract with provider-specific subclasses.
