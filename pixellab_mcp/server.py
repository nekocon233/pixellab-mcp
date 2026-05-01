"""
Pixel Lab MCP Server – V2 REST API edition
===========================================

Wraps all PixelLab V2 REST API endpoints as MCP tools via FastMCP.

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

from pixellab_mcp.tools import generate, rotate, animate, edit, character, tiles, objects, management  # noqa: E402

generate.register(mcp)
rotate.register(mcp)
animate.register(mcp)
edit.register(mcp)
character.register(mcp)
tiles.register(mcp)
objects.register(mcp)
management.register(mcp)


# ── Account balance ───────────────────────────────────────────────────────────

@mcp.tool()
async def get_balance() -> str:
    """Return the prepaid Pixel Lab credit balance in USD.

    DO NOT call this proactively before or after generation tools. Subscription
    users always show 0 USD here (subscription quota is tracked separately and
    is NOT reported by this endpoint), so a 0 result does NOT mean generation
    will fail. Only call this tool when the user explicitly asks about their
    prepaid credit balance.
    """
    from pixellab_mcp.tools import http_client
    result = await http_client.get("balance")
    credits = result.get("credits", {})
    usd = credits.get("usd", 0)
    subscription = result.get("subscription", {})
    gens = subscription.get("generations", "N/A")
    total = subscription.get("total", "N/A")
    return (
        f"Prepaid credit balance: {usd} USD\n"
        f"Subscription quota: {gens}/{total} generations"
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """Console script entry point (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
