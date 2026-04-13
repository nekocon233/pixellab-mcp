# pixellab-mcp

MCP server that wraps the **PixelLab private WebSocket API** — all 44+ pixel-art generation endpoints exposed as MCP tools.  
Equivalent in capability to the official Aseprite plugin, including the high-quality "Create images from style references" (Pro) feature.

## Quick start

No clone needed — run directly from GitHub with [uv](https://docs.astral.sh/uv/):

```bash
uvx --from git+https://github.com/nekocon233/pixellab-mcp pixellab-mcp
```

Or install once and call the console script:

```bash
pip install git+https://github.com/nekocon233/pixellab-mcp
pixellab-mcp
```

## Requirements

- Python 3.11+
- A [Pixel Lab](https://pixellab.ai) account with API access
- `uv` (recommended) or `pip`

## MCP client configuration

Set `PIXELLAB_SECRET` in the `env` block — no `.env` file needed. `PIXELLAB_TIER` and `PIXELLAB_VERSION` are optional (see [Environment variables](#environment-variables)).

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "pixellab": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/nekocon233/pixellab-mcp", "pixellab-mcp"],
      "env": {
        "PIXELLAB_SECRET": "your-token-here"
      }
    }
  }
}
```

### VS Code (`settings.json`)

```json
{
  "mcp": {
    "servers": {
      "pixellab": {
        "type": "stdio",
        "command": "uvx",
        "args": ["--from", "git+https://github.com/nekocon233/pixellab-mcp", "pixellab-mcp"],
        "env": {
          "PIXELLAB_SECRET": "your-token-here"
        }
      }
    }
  }
}
```

### Cursor / Windsurf / other MCP clients

Same pattern — `command: uvx`, `args: ["--from", "git+https://...", "pixellab-mcp"]`, `env.PIXELLAB_SECRET`.

## Local development

```bash
git clone https://github.com/nekocon233/pixellab-mcp
cd pixellab-mcp
pip install -e .
cp .env.example .env   # then fill in PIXELLAB_SECRET
pixellab-mcp
```

## Tool catalogue

### 🎨 Generate (8 tools)

| Tool                          | Description                                                                                                                                                |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `consistent_style_generate`   | **Best style-matching** — generates frames that match a reference sprite's visual style (equivalent to Aseprite Pro "Create images from style references") |
| `pixflux_same_style_generate` | Flux model single-frame generation from a style reference                                                                                                  |
| `pixelart_flux_generate`      | General Pixelart Flux generation from text                                                                                                                 |
| `style_generate`              | Full-control generation: pose reference, style image, palette, outline/shading control                                                                     |
| `spritesheet_generate`        | Full character spritesheet (n_rows × n_columns grid)                                                                                                       |
| `general_generate`            | General pixel art scenes and backgrounds                                                                                                                   |
| `general_xl_generate`         | Large-format scenes using the XL model                                                                                                                     |
| `image_to_pixelart`           | Convert any photo/artwork to pixel art                                                                                                                     |

### 🔄 Rotate (5 tools)

| Tool                       | Description                                             |
| -------------------------- | ------------------------------------------------------- |
| `rotate_single`            | Rotate a sprite by a specific angle offset              |
| `rotations_generate`       | Fill in missing cardinal directions from existing views |
| `four_rotations_generate`  | Generate 4-directional frames from text                 |
| `eight_rotations_generate` | Generate 8-directional frames from text                 |
| `reference_to_8_rotations` | Generate all 8 rotations from a concept + style image   |

### 🎬 Animate (8 tools)

| Tool                         | Description                                            |
| ---------------------------- | ------------------------------------------------------ |
| `movement_generate`          | walk / run / attack animations with movement reference |
| `animate_with_text`          | Quick text-driven character animation                  |
| `animate_with_text_v3`       | Higher-quality text animation (even frame count 4–16)  |
| `animation_generate`         | Skeleton-driven animation from text                    |
| `animate_character_object`   | Animate objects (bounce, explode, spin…)               |
| `interpolation_generate`     | In-between frames between two sprites                  |
| `interpolation_v3_generate`  | Higher-quality interpolation                           |
| `interpolation_pro_generate` | Pro interpolation                                      |

### ✏️ Edit (12 tools)

| Tool                     | Description                                         |
| ------------------------ | --------------------------------------------------- |
| `edit_generate`          | Text-guided edit of a single image                  |
| `edit_image_pro`         | Advanced single-image editing (Pro)                 |
| `edit_animation_pro`     | Edit all frames of an animation consistently        |
| `multi_edit_generate`    | Apply one edit instruction to multiple images       |
| `inpainting_generate`    | Fill a white-masked region with generated content   |
| `inpainting_v3_generate` | Improved inpainting (v3)                            |
| `correct_pixelart`       | Fix artifacts and mixed pixels in pixel art         |
| `remove_background`      | Remove background from a sprite                     |
| `reshape_generate`       | Reshape a character to match a target silhouette    |
| `resize_generate`        | Intelligent content-aware resize                    |
| `try_on_generate`        | Apply an outfit from one image to another character |
| `transfer_outfit_pro`    | Transfer outfit across all animation frames         |

### 👤 Character / Pose (4 tools)

| Tool                          | Description                                                      |
| ----------------------------- | ---------------------------------------------------------------- |
| `complete_character_generate` | Full animated character (all directions + animation) in one call |
| `re_pose_animation`           | Re-pose an animation frame via skeleton control                  |
| `pose_generate`               | Generate a character in a given pose                             |
| `pose_animation_generate`     | Multi-frame animation driven by pose images                      |

### 🗺️ Tiles (6 tools)

| Tool                            | Description                                          |
| ------------------------------- | ---------------------------------------------------- |
| `tiles_generate`                | Single seamless tile from text                       |
| `tiles_pro_generate`            | Professional tiles including isometric types         |
| `tiles_style_generate`          | Tileable map tile with visual style from a reference |
| `tileset_generate`              | Full Wang tileset (inner / outer / transition)       |
| `tileset_sidescroller_generate` | Side-scroller platform tileset                       |
| `texture_generate`              | Seamless repeating texture                           |

### 🔧 Utilities (1 tool)

| Tool             | Description                                   |
| ---------------- | --------------------------------------------- |
| `canny_generate` | Generate pixel art guided by a Canny edge map |
| `get_balance`    | Show current API credit balance               |

## Output

All generated images are saved to `assets/output/` with timestamped filenames.  
Tools return the saved path(s) as text.

## Environment variables

| Variable           | Required | Default | Description        |
| ------------------ | -------- | ------- | ------------------ |
| `PIXELLAB_SECRET`  | ✅        | —       | API secret key     |
| `PIXELLAB_TIER`    | ❌        | `1`     | Account tier       |
| `PIXELLAB_VERSION` | ❌        | `0.5.0` | API version string |

## Project structure

```
pixellab-mcp/
├── .env                  ← PIXELLAB_SECRET (not committed)
├── pyproject.toml        ← package metadata + entry point
├── assets/
│   └── output/           ← generated images saved here
└── pixellab_mcp/
    ├── server.py         ← FastMCP server + tool registration
    ├── __main__.py       ← python -m pixellab_mcp
    └── tools/
        ├── ws_client.py  ← WebSocket transport (auth injected automatically)
        ├── image_utils.py
        ├── generate.py
        ├── rotate.py
        ├── animate.py
        ├── edit.py
        ├── character.py
        ├── tiles.py
        └── utils.py
```

## Technical notes

- **Transport**: Private WebSocket API `ws://api.pixellab.ai/<endpoint>` (same backend as Aseprite plugin)
- **Auth**: `secret` / `tier` / `version` injected automatically from environment variables (via `.env` or MCP client `env` block)
- **Image encoding**: `generate-consistent-style` uses raw RGBA bytes (not PNG) — handled transparently by `image_utils`
- **No public REST API**: This server bypasses the limited `/v1/` REST API and calls the full private endpoint set

## License

Private use. PixelLab API usage subject to [PixelLab Terms of Service](https://pixellab.ai).
