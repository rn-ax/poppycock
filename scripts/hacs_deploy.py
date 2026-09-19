"""Tell a running Home Assistant instance's HACS to sync a repo to its latest commit.

This is the local-dev/testable copy -- ha-integration-ci.yml's `deploy` job
runs its own inlined copy of this same logic instead of checking out and
running this file directly, since that job executes in the *calling*
repo's context (e.g. ha-gym-tracker) and poppycock is private, so a real
checkout of poppycock from there has no read access. Keep the two in sync
by hand when either changes; `mise.toml` in this repo pins the Python
version for running/testing this file locally.

Assumes the target repo
is already registered as a HACS custom repository (a one-time manual setup
step, not done here) -- this only re-syncs an already-tracked repo.

Uses HACS's own websocket commands rather than the REST-callable
update.install service: HACS's install step installs whatever version it
last cached as available, not necessarily a fresh check, so
hacs/repositories/list is called first to force that check before
hacs/repository/download.

Deliberately does not restart Home Assistant afterward -- the new code
won't be loaded until that happens, done manually.

Reads FULL_NAME, CATEGORY, HOME_ASSISTANT_URL, and HOME_ASSISTANT_TOKEN
from the environment.
"""

import asyncio
import json
import os
import sys

import websockets


async def send(ws, msg_id, payload):
    payload["id"] = msg_id
    await ws.send(json.dumps(payload))
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=30)
        data = json.loads(raw)
        if data.get("id") == msg_id:
            return data


async def main():
    full_name = os.environ["FULL_NAME"]
    category = os.environ.get("CATEGORY") or "integration"
    token = os.environ["HOME_ASSISTANT_TOKEN"]
    base_url = os.environ["HOME_ASSISTANT_URL"]
    ws_scheme = "wss" if base_url.startswith("https") else "ws"
    host_part = base_url.split("://", 1)[1]
    uri = f"{ws_scheme}://{host_part}/api/websocket"

    async with websockets.connect(uri, max_size=50 * 1024 * 1024) as ws:
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        auth_result = json.loads(await ws.recv())
        if auth_result.get("type") != "auth_ok":
            print("auth failed", file=sys.stderr)
            raise SystemExit(1)

        msg_id = 1
        list_result = await send(ws, msg_id, {
            "type": "hacs/repositories/list",
            "categories": [category],
        })
        msg_id += 1
        repos = list_result.get("result", [])
        match = [r for r in repos if r.get("full_name", "").lower() == full_name.lower()]
        if not match:
            print(
                f"'{full_name}' is not registered as a HACS custom repository -- "
                "add it manually first.",
                file=sys.stderr,
            )
            raise SystemExit(1)

        repo_id = match[0]["id"]
        download_result = await send(ws, msg_id, {
            "type": "hacs/repository/download",
            "repository": repo_id,
        })
        if not download_result.get("success"):
            print("download failed:", json.dumps(download_result), file=sys.stderr)
            raise SystemExit(1)
        print(f"Updated {full_name} to latest main. Restart Home Assistant to load it.")


if __name__ == "__main__":
    asyncio.run(main())
