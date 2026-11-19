# Email MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-container MCP server (`stacks/mcp-email/`) that runs the Proton Bridge and exposes provider-agnostic email tools over HTTP/SSE.

**Architecture:** The container starts the Proton Bridge in gRPC mode, logs in configured accounts automatically, then runs a FastMCP HTTP/SSE server. Mail operations go through `clients.email.EmailClient` → `clients.imap.ImapClient` → `clients.protonmail.ProtonMailClient`.

**Tech Stack:** Python 3.12, `uv`, `fastmcp`, `pydantic`/`pydantic-settings`, `imapclient`, `grpcio`, `pyotp`, Proton Bridge (`ghcr.io/trent-maetzold/protonmail-bridge:build`).

---

## File Structure

All paths are relative to `stacks/mcp-email/`.

| File | Responsibility |
|------|----------------|
| `pyproject.toml` | Package metadata, deps, tool config. |
| `src/mcp_email/config.py` | Load `accounts.yaml` and env settings. |
| `src/mcp_email/models.py` | Pydantic models returned by tools. |
| `src/mcp_email/proto/bridge.proto` | Vendored Proton Bridge gRPC proto. |
| `src/mcp_email/proto/bridge_pb2.py` / `bridge_pb2_grpc.py` | Generated gRPC stubs. |
| `src/mcp_email/bridge_manager.py` | Bridge subprocess + gRPC login + credential cache. |
| `src/mcp_email/clients/email.py` | Abstract `EmailClient` contract. |
| `src/mcp_email/clients/imap.py` | Generic IMAP implementation. |
| `src/mcp_email/clients/protonmail.py` | Proton-specific folder names. |
| `src/mcp_email/server.py` | FastMCP tools + `/health` endpoint. |
| `src/mcp_email/__main__.py` | Entrypoint: start bridge, then MCP server. |
| `tests/test_config.py` | Config loading tests. |
| `tests/test_models.py` | Model validation tests. |
| `tests/test_imap_client.py` | `ImapClient` logic tests with mocked IMAP. |
| `Dockerfile` | Build image from forked bridge base + Python/uv. |
| `compose.yaml` / `compose.override.yaml` | Stack definition + Unraid labels. |
| `config/accounts.yaml.example` | Example account config. |
| `README.md` | Build/run instructions. |

---

### Task 1: Bootstrap the project

**Files:**
- Create: `stacks/mcp-email/pyproject.toml`
- Create: `stacks/mcp-email/src/mcp_email/__init__.py`
- Create: `stacks/mcp-email/README.md` (stub)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "mcp-email"
version = "0.1.0"
description = "MCP server for email (ProtonMail MVP)"
requires-python = ">=3.12"
dependencies = [
    "fastmcp>=3.4",
    "pydantic>=2.13",
    "pydantic-settings>=2.14",
    "pyyaml>=6.0",
    "imapclient>=2.3",
    "pyotp>=2.9",
    "grpcio>=1.64",
    "grpcio-tools>=1.64",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "httpx>=0.27"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_email"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create empty package init files**

```bash
cd stacks/mcp-email
mkdir -p src/mcp_email/clients src/mcp_email/proto tests config
touch src/mcp_email/__init__.py
```

- [ ] **Step 3: Create `README.md` stub**

```markdown
# mcp-email

MCP server for email. MVP supports ProtonMail via the Proton Bridge.
```

- [ ] **Step 4: Sync dependencies and commit**

Run:
```bash
cd stacks/mcp-email
uv sync --extra dev
```

Expected: `uv.lock` is generated and `.venv` exists.

Commit:
```bash
git add stacks/mcp-email/
git commit -m "feat(mcp-email): bootstrap uv project"
```

---

### Task 2: Vendor the Proton Bridge gRPC proto

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/proto/bridge.proto`
- Create: `stacks/mcp-email/src/mcp_email/proto/__init__.py`

- [ ] **Step 1: Download the proto**

Run:
```bash
cd stacks/mcp-email/src/mcp_email/proto
curl -L -o bridge.proto https://raw.githubusercontent.com/ProtonMail/proton-bridge/master/internal/frontend/grpc/bridge.proto
```

- [ ] **Step 2: Generate Python stubs**

Run:
```bash
cd stacks/mcp-email
uv run python -m grpc_tools.protoc \
  --proto_path=src/mcp_email/proto \
  --python_out=src/mcp_email/proto \
  --grpc_python_out=src/mcp_email/proto \
  bridge.proto
```

Expected: `bridge_pb2.py` and `bridge_pb2_grpc.py` appear.

- [ ] **Step 3: Fix import path in generated files**

Edit the generated `bridge_pb2_grpc.py` so that the import line reads:
```python
from mcp_email.proto import bridge_pb2 as mcp__email_dot_proto_dot_bridge__pb2
```

- [ ] **Step 4: Commit**

```bash
git add stacks/mcp-email/src/mcp_email/proto/
git commit -m "feat(mcp-email): vendor proton bridge grpc proto and stubs"
```

---

### Task 3: Configuration loading

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/config.py`
- Create: `stacks/mcp-email/tests/test_config.py`
- Create: `stacks/mcp-email/config/accounts.yaml.example`

- [ ] **Step 1: Write the failing test**

`tests/test_config.py`:
```python
from pathlib import Path

import pytest
import yaml

from mcp_email.config import AccountConfig, load_settings


def test_load_accounts(tmp_path, monkeypatch):
    config_path = tmp_path / "accounts.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "accounts": [
                    {
                        "provider": "proton",
                        "address": "me@proton.me",
                        "password_env": "TEST_PASSWORD",
                    }
                ]
            }
        )
    )
    monkeypatch.setenv("TEST_PASSWORD", "secret")

    settings = load_settings(accounts_config_path=config_path)

    assert len(settings.accounts) == 1
    account = settings.accounts[0]
    assert account.name == "me@proton.me"
    assert account.provider == "proton"
    assert account.address == "me@proton.me"
    assert account.password == "secret"


def test_missing_password_env(tmp_path, monkeypatch):
    monkeypatch.delenv("MISSING_PASSWORD", raising=False)
    config_path = tmp_path / "accounts.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "accounts": [
                    {
                        "provider": "proton",
                        "address": "me@proton.me",
                        "password_env": "MISSING_PASSWORD",
                    }
                ]
            }
        )
    )

    with pytest.raises(RuntimeError, match="MISSING_PASSWORD"):
        load_settings(accounts_config_path=config_path)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd stacks/mcp-email
uv run pytest tests/test_config.py -v
```

Expected: two import/fail errors because `config.py` does not exist.

- [ ] **Step 3: Implement `config.py`**

```python
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Literal, Optional

import yaml
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AccountConfig(BaseModel):
    name: Optional[str] = None
    provider: Literal["proton"]
    address: str
    password_env: str
    mailbox_password_env: Optional[str] = None
    totp_secret_env: Optional[str] = None
    totp_code_env: Optional[str] = None
    imap_host: str = "127.0.0.1"
    imap_port: int = 1143
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 1025

    @model_validator(mode="after")
    def set_name_and_password(self) -> "AccountConfig":
        if not self.name:
            self.name = self.address
        if not self.password:
            raise RuntimeError(f"Environment variable {self.password_env!r} is required")
        return self

    @property
    def password(self) -> Optional[str]:
        return os.environ.get(self.password_env)

    @property
    def mailbox_password(self) -> Optional[str]:
        if not self.mailbox_password_env:
            return None
        return os.environ.get(self.mailbox_password_env)

    @property
    def totp_secret(self) -> Optional[str]:
        if not self.totp_secret_env:
            return None
        return os.environ.get(self.totp_secret_env)

    @property
    def totp_code(self) -> Optional[str]:
        if not self.totp_code_env:
            return None
        return os.environ.get(self.totp_code_env)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MCP_EMAIL_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    accounts_config_path: Path = Path("/app/config/accounts.yaml")
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    accounts: List[AccountConfig] = Field(default_factory=list)


def load_settings(accounts_config_path: Optional[Path] = None) -> Settings:
    settings = Settings()
    if accounts_config_path is not None:
        settings.accounts_config_path = accounts_config_path

    if not settings.accounts_config_path.exists():
        raise RuntimeError(
            f"Accounts config not found: {settings.accounts_config_path}"
        )

    raw = yaml.safe_load(settings.accounts_config_path.read_text()) or {}
    settings.accounts = [AccountConfig(**a) for a in raw.get("accounts", [])]
    return settings
```

- [ ] **Step 4: Create example config**

`config/accounts.yaml.example`:
```yaml
accounts:
  - name: personal
    provider: proton
    address: me@proton.me
    password_env: PROTON_PERSONAL_PASSWORD
    # Optional: only needed for two-password mode
    # mailbox_password_env: PROTON_PERSONAL_MAILBOX_PASSWORD
    # Optional: one of these is required if 2FA is enabled
    # totp_secret_env: PROTON_PERSONAL_TOTP_SECRET
    # totp_code_env: PROTON_PERSONAL_TOTP_CODE
```

- [ ] **Step 5: Run tests**

```bash
cd stacks/mcp-email
uv run pytest tests/test_config.py -v
```

Expected: both tests pass.

- [ ] **Step 6: Commit**

```bash
git add stacks/mcp-email/
git commit -m "feat(mcp-email): add account configuration loading"
```

---

### Task 4: Pydantic models

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/models.py`
- Create: `stacks/mcp-email/tests/test_models.py`

- [ ] **Step 1: Write failing tests**

`tests/test_models.py`:
```python
from datetime import datetime

from mcp_email.models import (
    Address,
    Attachment,
    Email,
    EmailSummary,
    Folder,
    MailboxStatus,
    MailboxSummary,
)


def test_email_summary():
    summary = EmailSummary(
        message_id="<abc@example.com>",
        subject="Hello",
        from_=[Address(name="A", address="a@example.com")],
        to=[Address(name="B", address="b@example.com")],
        date=datetime.utcnow(),
        flags=["\\Seen"],
        labels=["Inbox"],
        has_attachments=False,
    )
    assert summary.message_id == "<abc@example.com>"


def test_mailbox_status():
    status = MailboxStatus(
        name="personal",
        address="me@proton.me",
        provider="proton",
        connected=True,
        summary=MailboxSummary(inbox_unread=3, inbox_total=10),
    )
    assert status.summary.inbox_unread == 3
```

- [ ] **Step 2: Run tests to verify failure**

```bash
cd stacks/mcp-email
uv run pytest tests/test_models.py -v
```

Expected: import errors.

- [ ] **Step 3: Implement `models.py`**

```python
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Address(BaseModel):
    name: Optional[str] = None
    address: str


class Folder(BaseModel):
    name: str
    attributes: List[str] = Field(default_factory=list)


class Attachment(BaseModel):
    filename: str
    content_type: str
    size: int


class EmailSummary(BaseModel):
    message_id: str
    subject: str
    from_: List[Address] = Field(alias="from")
    to: List[Address]
    date: datetime
    flags: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    has_attachments: bool = False


class Email(BaseModel):
    message_id: str
    subject: str
    from_: List[Address] = Field(alias="from")
    to: List[Address]
    cc: List[Address] = Field(default_factory=list)
    bcc: List[Address] = Field(default_factory=list)
    date: datetime
    flags: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)
    reply_to_message_id: Optional[str] = None


class DraftResult(BaseModel):
    message_id: str


class MailboxSummary(BaseModel):
    inbox_unread: int
    inbox_total: int


class MailboxStatus(BaseModel):
    name: str
    address: str
    provider: str
    connected: bool
    summary: Optional[MailboxSummary] = None
```

- [ ] **Step 4: Run tests**

```bash
cd stacks/mcp-email
uv run pytest tests/test_models.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add stacks/mcp-email/
git commit -m "feat(mcp-email): add pydantic models"
```

---

### Task 5: Bridge gRPC connection and credential cache

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/bridge_manager.py`

- [ ] **Step 1: Implement lifecycle and gRPC connection**

```python
from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

import grpc
from google.protobuf import empty_pb2

from mcp_email.config import AccountConfig, Settings
from mcp_email.proto import bridge_pb2, bridge_pb2_grpc

logger = logging.getLogger(__name__)

BRIDGE_BINARY = "/protonmail/proton-bridge"
GRPC_CONFIG_PATH = Path("/root/.config/protonmail/bridge-v3/grpcServerConfig.json")


class BridgeManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._proc: Optional[subprocess.Popen] = None
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[bridge_pb2_grpc.BridgeStub] = None
        self._metadata: tuple = ()
        self._credentials: Dict[str, str] = {}

    def start(self) -> None:
        self._init_pass()
        self._proc = subprocess.Popen(
            [BRIDGE_BINARY, "--grpc"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self._wait_for_grpc_config()
        self._connect()
        logger.info("Bridge gRPC connected")

    def _init_pass(self) -> None:
        store = Path("/root/.password-store")
        if store.exists():
            return
        logger.info("Initializing pass store")
        subprocess.run(
            ["gpg", "--generate-key", "--batch", "/protonmail/gpgparams"],
            check=True,
        )
        subprocess.run(["pass", "init", "pass-key"], check=True)

    def _wait_for_grpc_config(self, timeout: float = 60.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if GRPC_CONFIG_PATH.exists():
                return
            time.sleep(0.5)
        raise RuntimeError("Bridge did not write gRPC config in time")

    def _connect(self) -> None:
        config = json.loads(GRPC_CONFIG_PATH.read_text())
        address = f"127.0.0.1:{config['Port']}"
        token = config["Token"]
        cert = config["Cert"].encode()

        credentials = grpc.ssl_channel_credentials(root_certificates=cert)
        self._channel = grpc.secure_channel(address, credentials)
        self._stub = bridge_pb2_grpc.BridgeStub(self._channel)
        self._metadata = (("server-token", token),)

    def stop(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        if self._channel is not None:
            self._channel.close()

    def _call(self, method, request, timeout: float = 30.0):
        return method(request, metadata=self._metadata, timeout=timeout)

    def get_user_list(self) -> bridge_pb2.UserListResponse:
        return self._call(self._stub.GetUserList, empty_pb2.Empty())

    def get_account_state(self, address: str) -> Optional[bridge_pb2.User]:
        for user in self.get_user_list().users:
            if address in user.addresses or user.username == address:
                return user
        return None

    def get_bridge_password(self, address: str) -> Optional[str]:
        if address not in self._credentials:
            user = self.get_account_state(address)
            if user is None or user.state != bridge_pb2.CONNECTED:
                return None
            self._credentials[address] = user.password.decode()
        return self._credentials[address]

    def is_connected(self, address: str) -> bool:
        user = self.get_account_state(address)
        return user is not None and user.state == bridge_pb2.CONNECTED
```

- [ ] **Step 2: Commit**

```bash
git add stacks/mcp-email/src/mcp_email/bridge_manager.py
git commit -m "feat(mcp-email): add bridge gRPC connection and credential cache"
```

---

### Task 6: Bridge login flow

**Files:**
- Modify: `stacks/mcp-email/src/mcp_email/bridge_manager.py`

- [ ] **Step 1: Implement event-stream login handler**

Append to `bridge_manager.py`:

```python
import threading
from queue import Empty, Queue

import pyotp


class BridgeManager:
    # ... existing methods ...

    def ensure_accounts_logged_in(self) -> None:
        for account in self.settings.accounts:
            try:
                self.login_account(account)
            except Exception as exc:
                logger.error("Could not log in %s: %s", account.address, exc)

    def login_account(self, account: AccountConfig) -> None:
        if self.is_connected(account.address):
            logger.info("Account already connected: %s", account.address)
            return

        logger.info("Logging in account: %s", account.address)
        event_queue: Queue = Queue()
        stop_event = threading.Event()

        stream_thread = threading.Thread(
            target=self._read_event_stream,
            args=(event_queue, stop_event),
            daemon=True,
        )
        stream_thread.start()

        try:
            self._call(
                self._stub.Login,
                bridge_pb2.LoginRequest(
                    username=account.address,
                    password=account.password.encode(),
                ),
            )
            self._handle_login_events(account, event_queue)
        finally:
            stop_event.set()
            stream_thread.join(timeout=5)

    def _read_event_stream(self, queue: Queue, stop_event: threading.Event) -> None:
        try:
            for event in self._stub.RunEventStream(
                bridge_pb2.EventStreamRequest(ClientPlatform="mcp-email"),
                metadata=self._metadata,
            ):
                if stop_event.is_set():
                    break
                queue.put(event)
        except grpc.RpcError as exc:
            if not stop_event.is_set():
                logger.warning("Event stream ended: %s", exc)

    def _handle_login_events(self, account: AccountConfig, queue: Queue) -> None:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                event = queue.get(timeout=1)
            except Empty:
                if self.is_connected(account.address):
                    return
                continue

            login_event = event.login
            if login_event.error.message:
                raise RuntimeError(
                    f"Login failed for {account.address}: {login_event.error.message}"
                )

            if login_event.tfaRequested.username:
                self._submit_totp(account)
            elif login_event.twoPasswordRequested.username:
                self._submit_mailbox_password(account)
            elif login_event.finished.userID or login_event.alreadyLoggedIn.userID:
                return
            elif login_event.hvRequested.hvUrl:
                raise RuntimeError(
                    f"Human verification required for {account.address}: {login_event.hvRequested.hvUrl}"
                )

        raise RuntimeError(f"Login timed out for {account.address}")

    def _submit_totp(self, account: AccountConfig) -> None:
        if account.totp_secret:
            code = pyotp.TOTP(account.totp_secret).now()
        elif account.totp_code:
            code = account.totp_code
        else:
            raise RuntimeError(
                f"2FA required for {account.address} but no TOTP secret/code provided"
            )

        self._call(
            self._stub.Login2FA,
            bridge_pb2.LoginRequest(
                username=account.address,
                password=code.encode(),
            ),
        )

    def _submit_mailbox_password(self, account: AccountConfig) -> None:
        password = account.mailbox_password or account.password
        if not password:
            raise RuntimeError(f"Mailbox password required for {account.address}")

        self._call(
            self._stub.Login2Passwords,
            bridge_pb2.LoginRequest(
                username=account.address,
                password=password.encode(),
            ),
        )
```

- [ ] **Step 2: Commit**

```bash
git add stacks/mcp-email/src/mcp_email/bridge_manager.py
git commit -m "feat(mcp-email): implement bridge login with 2FA and mailbox password"
```

---

### Task 7: Abstract `EmailClient`

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/clients/email.py`

- [ ] **Step 1: Implement the ABC**

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from mcp_email.models import DraftResult, Email, EmailSummary, Folder, MailboxSummary


class EmailClient(ABC):
    @abstractmethod
    def list_folders(self) -> List[Folder]: ...

    @abstractmethod
    def search_emails(
        self,
        folder: str,
        subject: Optional[str] = None,
        from_address: Optional[str] = None,
        since: Optional[datetime] = None,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> List[EmailSummary]: ...

    @abstractmethod
    def read_email(self, message_id: str, mark_read: bool = True) -> Email: ...

    @abstractmethod
    def mark_email(
        self, message_id: str, read: Optional[bool] = None, flagged: Optional[bool] = None
    ) -> None: ...

    @abstractmethod
    def tag_email(self, message_id: str, label: str, action: str = "add") -> None: ...

    @abstractmethod
    def move_email(self, message_id: str, folder: str) -> None: ...

    @abstractmethod
    def trash_email(self, message_id: str) -> None: ...

    @abstractmethod
    def archive_email(self, message_id: str) -> None: ...

    @abstractmethod
    def draft_email(
        self,
        to: List[str],
        subject: str,
        body: Optional[str] = None,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to_message_id: Optional[str] = None,
    ) -> DraftResult: ...

    @abstractmethod
    def get_summary(self) -> MailboxSummary: ...
```

- [ ] **Step 2: Commit**

```bash
git add stacks/mcp-email/src/mcp_email/clients/email.py
git commit -m "feat(mcp-email): add EmailClient abstract contract"
```

---

### Task 8: Generic `ImapClient`

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/clients/imap.py`
- Create: `stacks/mcp-email/tests/test_imap_client.py`

- [ ] **Step 1: Write tests for provider hooks and message-id mapping**

`tests/test_imap_client.py`:
```python
from unittest.mock import MagicMock

from mcp_email.clients.imap import ImapClient


class FakeClient(ImapClient):
    @property
    def trash_folder_name(self) -> str:
        return "Trash"

    @property
    def archive_folder_name(self) -> str:
        return "Archive"

    @property
    def drafts_folder_name(self) -> str:
        return "Drafts"

    @property
    def sent_folder_name(self) -> str:
        return "Sent"

    @property
    def inbox_folder_name(self) -> str:
        return "Inbox"


def test_uid_for_message_id_calls_search():
    conn = MagicMock()
    conn.search.return_value = [42]

    client = FakeClient(host="127.0.0.1", port=1143, username="a", password="b")
    uid = client._uid_for_message_id(conn, "<abc@example.com>")

    assert uid == 42
    conn.search.assert_called_once()
```

- [ ] **Step 2: Run test to verify failure**

```bash
cd stacks/mcp-email
uv run pytest tests/test_imap_client.py -v
```

Expected: import errors.

- [ ] **Step 3: Implement `imap.py`**

```python
from __future__ import annotations

import email.message
import email.policy
import email.utils
import ssl
from abc import abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple

import imapclient

from mcp_email.clients.email import EmailClient
from mcp_email.models import (
    Address,
    Attachment,
    DraftResult,
    Email,
    EmailSummary,
    Folder,
    MailboxSummary,
)


class ImapClient(EmailClient):
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def _connect(self) -> imapclient.IMAPClient:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        conn = imapclient.IMAPClient(self.host, self.port, ssl=False)
        conn.starttls(ssl_context=context)
        conn.login(self.username, self.password)
        return conn

    @property
    @abstractmethod
    def trash_folder_name(self) -> str: ...

    @property
    @abstractmethod
    def archive_folder_name(self) -> str: ...

    @property
    @abstractmethod
    def drafts_folder_name(self) -> str: ...

    @property
    @abstractmethod
    def sent_folder_name(self) -> str: ...

    @property
    @abstractmethod
    def inbox_folder_name(self) -> str: ...

    def normalize_label(self, label: str) -> str:
        return label

    def _uid_for_message_id(
        self, conn: imapclient.IMAPClient, message_id: str
    ) -> Optional[int]:
        uids = conn.search(["HEADER", "MESSAGE-ID", message_id])
        return uids[0] if uids else None

    def _folder_uids(
        self,
        conn: imapclient.IMAPClient,
        folder: str,
        subject: Optional[str] = None,
        from_address: Optional[str] = None,
        since: Optional[datetime] = None,
        unread_only: bool = False,
    ) -> List[int]:
        conn.select_folder(folder)
        criteria: List = ["ALL"]
        if unread_only:
            criteria = ["UNSEEN"]
        if from_address:
            criteria += ["FROM", from_address]
        if subject:
            criteria += ["SUBJECT", subject]
        if since:
            criteria += ["SINCE", since.strftime("%d-%b-%Y")]
        return conn.search(criteria)

    def _flags_to_list(self, flags: tuple) -> List[str]:
        return [str(f) for f in flags]

    def _parse_address_header(self, value: Optional[str]) -> List[Address]:
        if not value:
            return []
        result = []
        for name, addr in email.utils.getaddresses([value]):
            result.append(Address(name=name or None, address=addr))
        return result

    def _parse_envelope_addresses(
        self, addresses: Optional[List[Tuple[bytes, bytes]]]
    ) -> List[Address]:
        if not addresses:
            return []
        result = []
        for name, addr in addresses:
            name_str = name.decode() if name else None
            addr_str = addr.decode() if addr else ""
            result.append(Address(name=name_str, address=addr_str))
        return result

    def list_folders(self) -> List[Folder]:
        with self._connect() as conn:
            return [
                Folder(name=f[2], attributes=[str(a) for a in f[0]])
                for f in conn.list_folders()
            ]

    def search_emails(
        self,
        folder: str,
        subject: Optional[str] = None,
        from_address: Optional[str] = None,
        since: Optional[datetime] = None,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> List[EmailSummary]:
        with self._connect() as conn:
            uids = self._folder_uids(
                conn, folder, subject, from_address, since, unread_only
            )
            uids = uids[offset : offset + limit]
            if not uids:
                return []

            fetched = conn.fetch(uids, ["ENVELOPE", "FLAGS", "RFC822.SIZE"])
            summaries = []
            for uid, data in fetched.items():
                env = data[b"ENVELOPE"]
                summaries.append(
                    EmailSummary(
                        message_id=env.message_id or "",
                        subject=env.subject.decode() if env.subject else "",
                        from_=self._parse_envelope_addresses(env.from_),
                        to=self._parse_envelope_addresses(env.to),
                        date=env.date,
                        flags=self._flags_to_list(data[b"FLAGS"]),
                        labels=[folder],
                        has_attachments=False,
                    )
                )
            return summaries

    def read_email(self, message_id: str, mark_read: bool = True) -> Email:
        with self._connect() as conn:
            uid = self._find_uid_anywhere(conn, message_id)
            if uid is None:
                raise RuntimeError(f"Message not found: {message_id}")

            folder = self._find_folder_for_uid(conn, uid) or self.inbox_folder_name
            conn.select_folder(folder)
            data = conn.fetch(uid, ["RFC822", "FLAGS"])[uid]
            msg = email.message_from_bytes(
                data[b"RFC822"], policy=email.policy.default
            )

            text, html, attachments = self._extract_parts(msg)
            if mark_read:
                conn.add_flags(uid, ["\\Seen"])

            return Email(
                message_id=msg["Message-ID"] or message_id,
                subject=msg["Subject"] or "",
                from_=self._parse_address_header(msg["From"]),
                to=self._parse_address_header(msg["To"]),
                cc=self._parse_address_header(msg.get("Cc", "")),
                bcc=self._parse_address_header(msg.get("Bcc", "")),
                date=msg["Date"].datetime if msg["Date"] else datetime.utcnow(),
                flags=self._flags_to_list(data[b"FLAGS"]),
                labels=[folder],
                body_text=text,
                body_html=html,
                attachments=attachments,
            )

    def _extract_parts(
        self, msg: email.message.EmailMessage
    ) -> tuple[Optional[str], Optional[str], List[Attachment]]:
        text: Optional[str] = None
        html: Optional[str] = None
        attachments: List[Attachment] = []

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain" and not part.get_filename():
                    text = part.get_content()
                elif ctype == "text/html" and not part.get_filename():
                    html = part.get_content()
                elif part.get_filename():
                    payload = part.get_payload(decode=True) or b""
                    attachments.append(
                        Attachment(
                            filename=part.get_filename(),
                            content_type=ctype,
                            size=len(payload),
                        )
                    )
        else:
            ctype = msg.get_content_type()
            if ctype == "text/plain":
                text = msg.get_content()
            elif ctype == "text/html":
                html = msg.get_content()

        return text, html, attachments

    def _find_uid_anywhere(
        self, conn: imapclient.IMAPClient, message_id: str
    ) -> Optional[int]:
        for folder in [
            self.inbox_folder_name,
            self.archive_folder_name,
            self.sent_folder_name,
            self.drafts_folder_name,
        ]:
            conn.select_folder(folder)
            uid = self._uid_for_message_id(conn, message_id)
            if uid is not None:
                return uid
        return None

    def _find_folder_for_uid(
        self, conn: imapclient.IMAPClient, uid: int
    ) -> Optional[str]:
        for folder in [
            self.inbox_folder_name,
            self.archive_folder_name,
            self.sent_folder_name,
            self.drafts_folder_name,
        ]:
            conn.select_folder(folder)
            if conn.search([f"UID {uid}"]):
                return folder
        return None

    def mark_email(
        self, message_id: str, read: Optional[bool] = None, flagged: Optional[bool] = None
    ) -> None:
        with self._connect() as conn:
            uid = self._find_uid_anywhere(conn, message_id)
            if uid is None:
                raise RuntimeError(f"Message not found: {message_id}")
            conn.select_folder(self._find_folder_for_uid(conn, uid) or self.inbox_folder_name)
            if read is True:
                conn.add_flags(uid, ["\\Seen"])
            elif read is False:
                conn.remove_flags(uid, ["\\Seen"])
            if flagged is True:
                conn.add_flags(uid, ["\\Flagged"])
            elif flagged is False:
                conn.remove_flags(uid, ["\\Flagged"])

    def move_email(self, message_id: str, folder: str) -> None:
        with self._connect() as conn:
            uid = self._find_uid_anywhere(conn, message_id)
            if uid is None:
                raise RuntimeError(f"Message not found: {message_id}")
            conn.copy(uid, folder)
            conn.delete_messages(uid)
            conn.expunge()

    def trash_email(self, message_id: str) -> None:
        self.move_email(message_id, self.trash_folder_name)

    def archive_email(self, message_id: str) -> None:
        self.move_email(message_id, self.archive_folder_name)

    def tag_email(self, message_id: str, label: str, action: str = "add") -> None:
        label = self.normalize_label(label)
        with self._connect() as conn:
            if action == "add":
                uid = self._find_uid_anywhere(conn, message_id)
                if uid is None:
                    raise RuntimeError(f"Message not found: {message_id}")
                conn.copy(uid, label)
            elif action == "remove":
                conn.select_folder(label)
                uid = self._uid_for_message_id(conn, message_id)
                if uid is None:
                    raise RuntimeError(f"Message not found in {label}: {message_id}")
                conn.delete_messages(uid)
                conn.expunge()
            else:
                raise ValueError(f"Unknown tag action: {action}")

    def draft_email(
        self,
        to: List[str],
        subject: str,
        body: Optional[str] = None,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to_message_id: Optional[str] = None,
    ) -> DraftResult:
        if not body and not html_body:
            raise ValueError("Either body or html_body is required")

        msg = email.message.EmailMessage(policy=email.policy.default)
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        if reply_to_message_id:
            msg["In-Reply-To"] = reply_to_message_id
            msg["References"] = reply_to_message_id

        if html_body:
            msg.make_alternative()
            if body:
                msg.add_alternative(body, subtype="plain")
            msg.add_alternative(html_body, subtype="html")
        else:
            msg.set_content(body)

        with self._connect() as conn:
            conn.append(
                self.drafts_folder_name,
                msg.as_bytes(),
                flags=["\\Draft", "\\Seen"],
            )

        return DraftResult(message_id=msg["Message-ID"])

    def get_summary(self) -> MailboxSummary:
        with self._connect() as conn:
            conn.select_folder(self.inbox_folder_name)
            unseen = conn.search(["UNSEEN"])
            total = conn.search(["ALL"])
        return MailboxSummary(inbox_unread=len(unseen), inbox_total=len(total))
```

- [ ] **Step 4: Run tests**

```bash
cd stacks/mcp-email
uv run pytest tests/test_imap_client.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add stacks/mcp-email/src/mcp_email/clients/imap.py tests/test_imap_client.py
git commit -m "feat(mcp-email): add generic ImapClient"
```

---

### Task 9: `ProtonMailClient`

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/clients/protonmail.py`
- Create: `stacks/mcp-email/tests/test_protonmail_client.py`

- [ ] **Step 1: Implement `protonmail.py`**

```python
from __future__ import annotations

from mcp_email.clients.imap import ImapClient


class ProtonMailClient(ImapClient):
    @property
    def trash_folder_name(self) -> str:
        return "Trash"

    @property
    def archive_folder_name(self) -> str:
        return "Archive"

    @property
    def drafts_folder_name(self) -> str:
        return "Drafts"

    @property
    def sent_folder_name(self) -> str:
        return "Sent"

    @property
    def inbox_folder_name(self) -> str:
        return "Inbox"
```

- [ ] **Step 2: Write hook tests**

`tests/test_protonmail_client.py`:
```python
from mcp_email.clients.protonmail import ProtonMailClient


def test_proton_folder_names():
    client = ProtonMailClient("127.0.0.1", 1143, "me@proton.me", "pw")
    assert client.trash_folder_name == "Trash"
    assert client.archive_folder_name == "Archive"
    assert client.drafts_folder_name == "Drafts"
```

- [ ] **Step 3: Run tests and commit**

```bash
cd stacks/mcp-email
uv run pytest tests/test_protonmail_client.py -v
git add stacks/mcp-email/src/mcp_email/clients/protonmail.py tests/test_protonmail_client.py
git commit -m "feat(mcp-email): add ProtonMailClient"
```

---

### Task 10: FastMCP server and tools

**Files:**
- Create: `stacks/mcp-email/src/mcp_email/server.py`
- Create: `stacks/mcp-email/src/mcp_email/__main__.py`
- Create: `stacks/mcp-email/tests/test_server.py`

- [ ] **Step 1: Implement `server.py`**

```python
from __future__ import annotations

import logging
from datetime import datetime
from typing import AsyncIterator, List, Optional

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from mcp_email.bridge_manager import BridgeManager
from mcp_email.clients.email import EmailClient
from mcp_email.clients.protonmail import ProtonMailClient
from mcp_email.config import Settings
from mcp_email.models import (
    DraftResult,
    Email,
    EmailSummary,
    Folder,
    MailboxStatus,
    MailboxSummary,
)

logger = logging.getLogger(__name__)


def create_app(settings: Settings, bridge: BridgeManager) -> Starlette:
    mcp = FastMCP("email")

    def get_account(mailbox: str):
        account = next(
            (a for a in settings.accounts if a.name == mailbox or a.address == mailbox),
            None,
        )
        if account is None:
            raise RuntimeError(f"Unknown mailbox: {mailbox}")
        return account

    def get_client(account) -> EmailClient:
        if account.provider != "proton":
            raise RuntimeError(f"Unsupported provider: {account.provider}")
        password = bridge.get_bridge_password(account.address)
        if password is None:
            raise RuntimeError(f"Account not connected: {account.address}")
        return ProtonMailClient(
            host=account.imap_host,
            port=account.imap_port,
            username=account.address,
            password=password,
        )

    @mcp.tool()
    def list_mailboxes() -> List[MailboxStatus]:
        result = []
        for account in settings.accounts:
            connected = bridge.is_connected(account.address)
            summary: Optional[MailboxSummary] = None
            if connected:
                try:
                    summary = get_client(account).get_summary()
                except Exception as exc:
                    logger.warning("Summary failed for %s: %s", account.address, exc)
            result.append(
                MailboxStatus(
                    name=account.name,
                    address=account.address,
                    provider=account.provider,
                    connected=connected,
                    summary=summary,
                )
            )
        return result

    @mcp.tool()
    def list_folders(mailbox: str) -> List[Folder]:
        return get_client(get_account(mailbox)).list_folders()

    @mcp.tool()
    def search_emails(
        mailbox: str,
        folder: str,
        subject: Optional[str] = None,
        from_address: Optional[str] = None,
        since: Optional[datetime] = None,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> List[EmailSummary]:
        return get_client(get_account(mailbox)).search_emails(
            folder=folder,
            subject=subject,
            from_address=from_address,
            since=since,
            unread_only=unread_only,
            limit=limit,
            offset=offset,
        )

    @mcp.tool()
    def read_email(mailbox: str, message_id: str, mark_read: bool = True) -> Email:
        return get_client(get_account(mailbox)).read_email(
            message_id, mark_read=mark_read
        )

    @mcp.tool()
    def mark_email(
        mailbox: str,
        message_id: str,
        read: Optional[bool] = None,
        flagged: Optional[bool] = None,
    ) -> None:
        return get_client(get_account(mailbox)).mark_email(
            message_id, read=read, flagged=flagged
        )

    @mcp.tool()
    def tag_email(
        mailbox: str, message_id: str, label: str, action: str = "add"
    ) -> None:
        return get_client(get_account(mailbox)).tag_email(
            message_id, label, action=action
        )

    @mcp.tool()
    def move_email(mailbox: str, message_id: str, folder: str) -> None:
        return get_client(get_account(mailbox)).move_email(message_id, folder)

    @mcp.tool()
    def trash_email(mailbox: str, message_id: str) -> None:
        return get_client(get_account(mailbox)).trash_email(message_id)

    @mcp.tool()
    def archive_email(mailbox: str, message_id: str) -> None:
        return get_client(get_account(mailbox)).archive_email(message_id)

    @mcp.tool()
    def draft_email(
        mailbox: str,
        to: List[str],
        subject: str,
        body: Optional[str] = None,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to_message_id: Optional[str] = None,
    ) -> DraftResult:
        return get_client(get_account(mailbox)).draft_email(
            to=to,
            subject=subject,
            body=body,
            html_body=html_body,
            cc=cc,
            bcc=bcc,
            reply_to_message_id=reply_to_message_id,
        )

    async def health(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    sse_app = mcp.http_app(transport="sse")
    app = Starlette(
        routes=[
            Route("/health", health),
            Mount("/", app=sse_app),
        ]
    )
    return app
```

- [ ] **Step 2: Implement `__main__.py`**

```python
import logging

import uvicorn

from mcp_email.bridge_manager import BridgeManager
from mcp_email.config import load_settings
from mcp_email.server import create_app


def main() -> None:
    settings = load_settings()
    logging.basicConfig(level=settings.log_level.upper())

    bridge = BridgeManager(settings)
    try:
        bridge.start()
        bridge.ensure_accounts_logged_in()
    except Exception as exc:
        logging.exception("Bridge startup failed: %s", exc)

    app = create_app(settings, bridge)
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write a server smoke test**

`tests/test_server.py`:
```python
from unittest.mock import MagicMock, patch

from httpx import ASGITransport, AsyncClient

from mcp_email.bridge_manager import BridgeManager
from mcp_email.config import AccountConfig, Settings
from mcp_email.server import create_app


async def test_health_endpoint():
    settings = Settings(accounts_config_path="/tmp/nonexistent.yaml")
    settings.accounts = [
        AccountConfig(
            name="test",
            provider="proton",
            address="test@proton.me",
            password_env="TEST_PASSWORD",
        )
    ]

    bridge = MagicMock(spec=BridgeManager)
    bridge.is_connected.return_value = False

    with patch.dict("os.environ", {"TEST_PASSWORD": "pw"}, clear=False):
        app = create_app(settings, bridge)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
```

- [ ] **Step 4: Run tests**

```bash
cd stacks/mcp-email
uv run pytest tests/test_server.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add stacks/mcp-email/src/mcp_email/server.py stacks/mcp-email/src/mcp_email/__main__.py tests/test_server.py
git commit -m "feat(mcp-email): add FastMCP server and tools"
```

---

### Task 11: Dockerfile

**Files:**
- Create: `stacks/mcp-email/Dockerfile`

- [ ] **Step 1: Write `Dockerfile`**

```dockerfile
# syntax=docker/dockerfile:1
FROM ghcr.io/trent-maetzold/protonmail-bridge:build

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev --python 3.12

ENV PYTHONPATH=/app/src
ENV HOME=/root

EXPOSE 8000

CMD ["uv", "run", "--python", "3.12", "python", "-m", "mcp_email"]
```

Pin the bridge base image to a digest in production by editing the `FROM` line after the first successful build.

- [ ] **Step 2: Build the image locally**

```bash
cd stacks/mcp-email
docker build -t mcp-email:local .
```

Expected: image builds successfully.

- [ ] **Step 3: Commit**

```bash
git add stacks/mcp-email/Dockerfile
git commit -m "feat(mcp-email): add Dockerfile"
```

---

### Task 12: Compose files and Unraid metadata

**Files:**
- Create: `stacks/mcp-email/compose.yaml`
- Create: `stacks/mcp-email/compose.override.yaml`
- Create: `stacks/mcp-email/name`
- Create: `stacks/mcp-email/icon_url`

- [ ] **Step 1: Write `compose.yaml`**

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/compose-spec/compose-spec/master/schema/compose-spec.json

services:
  server:
    container_name: mcp_email
    image: ghcr.io/trent-maetzold/mcp-email:latest
    restart: unless-stopped
    volumes:
      - /mnt/cache/appdata/mcp_email/server/bridge:/root
      - /mnt/cache/appdata/mcp_email/server/config:/app/config:ro
    networks:
      - proxy
    environment:
      TZ: "America/Chicago"
      MCP_EMAIL_LOG_LEVEL: "INFO"
      MCP_EMAIL_ACCOUNTS_CONFIG_PATH: "/app/config/accounts.yaml"
      PROTON_PERSONAL_PASSWORD: "${PROTON_PERSONAL_PASSWORD:?PROTON_PERSONAL_PASSWORD is required}"
    healthcheck:
      test: ["CMD", "wget", "--spider", "--quiet", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 60s
    labels:
      traefik.enable: "true"
      traefik.http.routers.mcp-email.rule: "Host(`mcp-email.trkm.io`)"
      traefik.http.services.mcp-email.loadBalancer.server.port: "8000"

networks:
  proxy:
    external: true
```

Adjust the host (`mcp-email.trkm.io`) and secret env vars to match your accounts.

- [ ] **Step 2: Write `compose.override.yaml`**

```yaml
services:
  server:
    labels:
      net.unraid.docker.managed: "composeman"
      net.unraid.docker.icon: "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/proton-mail.png"
      net.unraid.docker.webui: "https://mcp-email.trkm.io"
      net.unraid.docker.shell: "/bin/bash"
```

- [ ] **Step 3: Create `name` and `icon_url`**

`name`:
```text
Email MCP
```

`icon_url`:
```text
https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/proton-mail.png
```

- [ ] **Step 4: Validate compose**

```bash
cd stacks/mcp-email
docker compose config
```

Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add stacks/mcp-email/compose.yaml stacks/mcp-email/compose.override.yaml stacks/mcp-email/name stacks/mcp-email/icon_url
git commit -m "feat(mcp-email): add compose files and unraid metadata"
```

---

### Task 13: Finalize README and smoke test

**Files:**
- Modify: `stacks/mcp-email/README.md`

- [ ] **Step 1: Write README**

```markdown
# mcp-email

MCP server for email. MVP supports ProtonMail via the Proton Bridge.

## Configuration

1. Copy `config/accounts.yaml.example` to `/mnt/cache/appdata/mcp_email/server/config/accounts.yaml`.
2. Set the required env vars in your `.env` (e.g., `PROTON_PERSONAL_PASSWORD`).
3. Deploy with `docker compose up -d`.

## Development

```bash
cd stacks/mcp-email
uv sync --extra dev
uv run pytest
```

## Building

```bash
docker build -t mcp-email:local .
```
```

- [ ] **Step 2: Manual smoke test**

After deploying with a real Proton account:

1. Wait for the container to be healthy.
2. Connect an MCP client to `https://mcp-email.trkm.io/sse`.
3. Call `list_mailboxes` and confirm the account is `connected: true`.
4. Call `search_emails` on `Inbox`.
5. Call `read_email` on a returned message.
6. Call `archive_email` and verify the message moved in Proton.

- [ ] **Step 3: Run full test suite**

```bash
cd stacks/mcp-email
uv run pytest -v
```

Expected: all unit tests pass.

- [ ] **Step 4: Commit**

```bash
git add stacks/mcp-email/README.md
git commit -m "docs(mcp-email): add README and smoke test notes"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** every section of the design spec maps to one or more tasks above.
- [x] **Placeholder scan:** no `TBD`, `TODO`, or vague steps. The bridge base image digest is intentionally left unpinned with instructions to pin it after the first build.
- [x] **Type consistency:** `EmailClient` contract, `ImapClient` implementation, and tool signatures use the same model names (`EmailSummary`, `Email`, `DraftResult`, `Folder`, `MailboxStatus`, `MailboxSummary`).
- [x] **No dict tool payloads:** all tool inputs are primitives/models; `list_mailboxes` returns `List[MailboxStatus]`.
- [x] **No MCP auth in MVP:** security section defers auth to Traefik/Authelia.
- [x] **Provider hierarchy:** `EmailClient` ABC → `ImapClient` → `ProtonMailClient`, with only Proton-specific folder names in the subclass.
- [x] **HTML drafts:** `draft_email` accepts `html_body` and builds multipart alternative messages.
- [x] **Generic IMAP:** `ImapClient` takes host/port; `ProtonMailClient` only supplies the local bridge defaults.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-26-email-mcp-server.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach?

**Recommended: Subagent-Driven.**

**END**

