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
    """Return the current Pixel Lab account credit balance in USD."""
    client = _pl.Client(secret=os.getenv("PIXELLAB_SECRET", ""))
    balance = client.get_balance()
    return f"Balance: {balance.usd} USD"


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """Console script entry point (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
