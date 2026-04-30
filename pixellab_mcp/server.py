"""
Pixel Lab MCP Server – private WebSocket API edition
=====================================================

Wraps all 44+ PixelLab private WebSocket endpoints as MCP tools via FastMCP.

Run (stdio transport):
    pixellab-mcp                         # after pip install -e .
    python -m pixellab_mcp               # without installing
    uvx --from . pixellab-mcp            # one-shot with uv

Requirements: see pyproject.toml
"""
import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

if not os.getenv("PIXELLAB_SECRET"):
    print("ERROR: PIXELLAB_SECRET is not set in .env", file=sys.stderr)
    sys.exit(1)


# ── FastMCP server instance ───────────────────────────────────────────────────

mcp = FastMCP("pixellab-mcp")

# ── Register all tool groups ──────────────────────────────────────────────────

from pixellab_mcp.tools import generate, rotate, animate, edit, character, tiles, utils  # noqa: E402

generate.register(mcp)
rotate.register(mcp)
animate.register(mcp)
edit.register(mcp)
character.register(mcp)
tiles.register(mcp)
utils.register(mcp)

# ── Bonus: account balance via public SDK ─────────────────────────────────────

import pixellab as _pl  # noqa: E402



@mcp.tool()
def get_balance() -> str:
    """Return the prepaid Pixel Lab credit balance in USD.

    DO NOT call this proactively before or after generation tools. Subscription
    users always show 0 USD here (subscription quota is tracked separately and
    is NOT reported by this endpoint), so a 0 result does NOT mean generation
    will fail. Only call this tool when the user explicitly asks about their
    prepaid credit balance.
    """
    client = _pl.Client(secret=os.getenv("PIXELLAB_SECRET", ""))
    balance = client.get_balance()
    return f"Prepaid credit balance: {balance.usd} USD (subscription quota not included)"


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """Console script entry point (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
