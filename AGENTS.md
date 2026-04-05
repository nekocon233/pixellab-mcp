# AGENTS.md — pixellab-mcp

## Project overview

MCP server wrapping the PixelLab **private WebSocket API** (`ws://api.pixellab.ai/<endpoint>`).  
45 MCP tools covering pixel-art generation, rotation, animation, editing, characters, tiles, and utilities.

## Architecture

```
pixellab_mcp/
├── server.py          # FastMCP instance; registers all tool groups; console entry point
├── __main__.py        # python -m pixellab_mcp
└── tools/
    ├── ws_client.py   # Single async call() function; injects auth; handles WebSocket lifecycle
    ├── image_utils.py # path_to_png_b64 / path_to_rgba_b64 / save_response_images
    ├── generate.py    # Group A: image generation (8 tools)
    ├── rotate.py      # Group B: rotations (5 tools)
    ├── animate.py     # Group C: animation (8 tools)
    ├── edit.py        # Group D: editing / inpainting (12 tools)
    ├── character.py   # Group E: character / pose (4 tools)
    ├── tiles.py       # Group F: tiles / tilesets (6 tools)
    └── utils.py       # Group G: utilities (1 tool)
```

Each tool module exposes a single `register(mcp: FastMCP)` function; `server.py` calls them all at startup.

## Key conventions

### Adding a new tool

1. Find the correct group file in `pixellab_mcp/tools/`.
2. Add a new `@mcp.tool()` async function inside the `register(mcp)` function body.
3. Call `await ws_client.call("endpoint-name", payload)` — auth fields are injected automatically.
4. Use `image_utils.extract_images(result)` + `image_utils.save_response_images(...)` to save output.

### Image encoding rules

- **`generate-consistent-style`**: raw RGBA bytes — use `path_to_rgba_b64(path)` → returns `(b64, width, height)`.
- **All other endpoints**: PNG base64 — use `path_to_png_b64(path)`.
- Response images: `save_response_images()` auto-detects PNG vs raw RGBA by inspecting the PNG magic header.

### WebSocket payload auth

`ws_client.call()` automatically prepends:
```python
{"secret": SECRET, "tier": TIER, "version": VERSION, **your_payload}
```
`SECRET` from `.env`; `TIER` and `VERSION` from the Aseprite plugin `package.json` at  
`C:\Users\<user>\AppData\Roaming\Aseprite\extensions\pixellab\package.json`.

### Seed field

The private API expects `seed` as a **string** (e.g. `"0"`), not an integer. Always `str(seed)` before adding to payload.

### Output directory

All generated images are saved to `assets/output/` (created automatically).  
`image_utils.ensure_output_dir()` is called by `save_response_images()`.

## Build & run

```bash
pip install -e .          # install with console script
pixellab-mcp              # start server (stdio)
python -m pixellab_mcp   # alternative without console script
```

## Environment

| Variable          | Required | Description                    |
| ----------------- | -------- | ------------------------------ |
| `PIXELLAB_SECRET` | ✅        | API secret key — set in `.env` |

## Do not

- Do not commit `.env`.
- Do not use the public REST API (`https://api.pixellab.ai/v1/`) — this project uses the private WebSocket API.
- Do not add top-level scripts in the repo root — all code lives in `pixellab_mcp/`.
