# AGENTS.md — pixellab-mcp

## Project overview

MCP server wrapping the **PixelLab V2 REST API** (`https://api.pixellab.ai/v2/<endpoint>`).
46 MCP tools covering pixel-art generation, animation, editing, characters, tiles, objects, and management.

## Architecture

```
pixellab_mcp/
├── server.py          # FastMCP instance; registers all tool groups; console entry point
├── __main__.py        # python -m pixellab_mcp
└── tools/
    ├── http_client.py # REST HTTP client: call(), call_async(), get(), delete(), patch()
    ├── image_utils.py # path_to_png_b64 / path_to_rgba_b64 / save_response_images / extract_images
    ├── generate.py    # 7 tools: pixflux, bitforge, style, general, xl, image_to_pixelart
    ├── animate.py     # 5 tools: movement, animate_text, animate_text_v3, animation, interpolation
    ├── edit.py        # 9 tools: edit, edit_pro, edit_animation, multi_edit, inpaint, inpaint_v3, remove_bg, resize, transfer_outfit
    ├── character.py   # 5 tools: complete_char, estimate_skeleton, animate_skeleton, pose, pose_animation
    ├── rotate.py      # 5 tools: rotate_single, rotations, 4_rotations, 8_rotations, ref_to_8_rotations
    ├── tiles.py       # 4 tools: tileset, tileset_sidescroller, tiles_pro, isometric_tile
    ├── objects.py     # 2 tools: map_object, object_4_directions
    └── management.py  # 8 tools: character/object CRUD + balance
```

Each tool module exposes a single `register(mcp: FastMCP)` function; `server.py` calls them all at startup.

## Key conventions

### Adding a new tool

1. Find the correct group file in `pixellab_mcp/tools/`.
2. Add a new `@mcp.tool()` async function inside the `register(mcp)` function body.
3. For sync endpoints (return 200): `result = await http_client.call("endpoint-name", payload)`
4. For async endpoints (return 202 + background job): `result = await http_client.call_async("endpoint-name", payload)`
5. Use `image_utils.extract_images(result)` + `image_utils.save_response_images(...)` to save output.

### Two call modes

- **`http_client.call(endpoint, payload)`** — for sync V2 endpoints that return results immediately (200).
- **`http_client.call_async(endpoint, payload)`** — for async V2 endpoints that return a `background_job_id` (202). Automatically polls `GET /background-jobs/{id}` until complete.

### Image encoding

- Most endpoints: PNG base64 — use `image_utils.path_to_png_b64(path)`.
- Some endpoints (animate-with-text-v3, consistent-style): may need raw RGBA — use `image_utils.path_to_rgba_b64(path)`.
- Structured image fields: `{"base64": b64_string}` for simple, `{"image": {"base64": b64}, "size": {"width": w, "height": h}}` for structured.
- Response images: `save_response_images()` auto-detects PNG vs raw RGBA by inspecting the magic header.

### Auth

`http_client` automatically adds `Authorization: Bearer {PIXELLAB_SECRET}` header to all requests.
Only `PIXELLAB_SECRET` is required (no tier/version needed in V2).

### Seed field

V2 API accepts `seed` as an **integer** (not a string like the old WebSocket API).

### Output directory

Each tool accepts an `output_dir` parameter. `save_response_images()` creates the directory automatically.

## Build & run

```bash
pip install -e .          # install with console script
pixellab-mcp              # start server (stdio)
python -m pixellab_mcp   # alternative without console script
```

## Environment

| Variable          | Required | Description                       |
| ----------------- | -------- | --------------------------------- |
| `PIXELLAB_SECRET` | Yes      | API secret key (Bearer token)     |

## Do not

- Do not commit `.env`.
- Do not add top-level scripts in the repo root — all code lives in `pixellab_mcp/`.
- Do not import `ws_client` — it has been removed.
