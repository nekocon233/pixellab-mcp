# pixellab-mcp

MCP server wrapping the **PixelLab V2 REST API** — 61 pixel-art generation tools exposed as MCP tools.
Supports generation, animation, editing, character/object management, tiles, and more.

## Quick start

Run directly from GitHub with [uv](https://docs.astral.sh/uv/):

```bash
uvx --from git+https://github.com/nekocon233/pixellab-mcp pixellab-mcp
```

Or install and run the console script:

```bash
pip install git+https://github.com/nekocon233/pixellab-mcp
pixellab-mcp
```

## Requirements

- Python 3.11+
- A [PixelLab](https://pixellab.ai) account with API access
- `uv` (recommended) or `pip`

## MCP client configuration

Set `PIXELLAB_SECRET` in the `env` block.

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

### VS Code / Cursor (`settings.json`)

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

## Local development

```bash
git clone https://github.com/nekocon233/pixellab-mcp
cd pixellab-mcp
pip install -e .
cp .env.example .env   # then fill in PIXELLAB_SECRET
pixellab-mcp
```

## Tool catalogue

### Generate (9 tools)

| Tool | Description |
|---|---|
| `pixelart_flux_generate` | General pixel art from text (Pixflux model) |
| `consistent_style_generate` | Best style-matching — generates frames matching a reference |
| `pixflux_same_style_generate` | Single-frame generation from a style reference (Bitforge) |
| `style_generate` | Full-control generation with style transfer (Bitforge) |
| `general_generate` | General pixel art scenes and backgrounds |
| `general_xl_generate` | Large-format scenes up to 792x688 (Pro) |
| `image_to_pixelart` | Convert any photo/artwork to pixel art |
| `pixen_generate` | Pixel art generation using Pixen model (max 768x768, supports negative prompt) |
| `generate_ui_element` | Generate pixel art UI elements (buttons, health bars, icons, frames) |

### Animate (5 tools)

| Tool | Description |
|---|---|
| `movement_generate` | Walk / run / attack animations with character description |
| `animate_with_text` | Pro-quality text-driven character animation |
| `animate_with_text_v3` | Higher-quality text animation with optional end frame |
| `animation_generate` | Animation sequence from text + reference character |
| `interpolation_generate` | In-between frames morphing between two sprites |

### Edit (9 tools)

| Tool | Description |
|---|---|
| `edit_generate` | Text-guided edit of a single image |
| `edit_image_pro` | Advanced editing with text or reference (Pro) |
| `edit_animation_pro` | Edit all frames of an animation consistently |
| `multi_edit_generate` | Apply one edit instruction to multiple images |
| `inpainting_generate` | Fill a masked region with generated content |
| `inpainting_v3_generate` | Improved inpainting with separate mask (v3) |
| `remove_background` | Remove background from a sprite |
| `resize_generate` | Intelligent content-aware resize |
| `transfer_outfit_pro` | Transfer outfit across all animation frames |

### Character (6 tools)

| Tool | Description |
|---|---|
| `complete_character_generate` | Multi-direction character views (4 or 8 directions) |
| `estimate_skeleton` | Extract skeleton keypoints from a character image |
| `animate_with_skeleton` | Animate using skeleton pose control |
| `pose_generate` | Generate character in a specific skeleton pose |
| `pose_animation_generate` | Multi-frame animation driven by skeleton keypoints |
| `animate_character` | Animate existing character (created via complete_character_generate) |

### Rotate (6 tools)

| Tool | Description |
|---|---|
| `rotate_single` | Rotate a sprite by a specific angle offset |
| `rotations_generate` | Fill in missing cardinal directions from existing views |
| `four_rotations_generate` | Generate 4-directional frames from text |
| `eight_rotations_generate` | Generate 8-directional frames from text |
| `reference_to_8_rotations` | Generate all 8 rotations from concept + style image |
| `generate_8_rotations_v3` | Generate 8 rotations from a single reference frame (v3 quality) |

### Tiles (4 tools)

| Tool | Description |
|---|---|
| `tileset_generate` | Full Wang tileset (lower / upper / transition) |
| `tileset_sidescroller_generate` | Side-scroller platform tileset |
| `tiles_pro_generate` | Pro tiles: isometric, hex, octagon |
| `create_isometric_tile` | Single isometric tile (block / thick / thin) |

### Objects (6 tools)

| Tool | Description |
|---|---|
| `create_map_object` | Generate map object for top-down games (tree, rock, chest, etc.) |
| `create_object` | Create object using Objects pipeline (returns object_id) |
| `animate_object` | Animate existing object in a specific direction |
| `vary_object` | Create variation of existing object by text edit |
| `select_object_frames` | Promote selected frames of review-status object |
| `dismiss_object_review` | Dismiss review-status object without saving |

### Management (15 tools)

**Character Management:**

| Tool | Description |
|---|---|
| `list_characters` | List your characters (paginated) |
| `get_character` | Get character details + rotation URLs |
| `delete_character` | Delete a character |
| `export_character_zip` | Export character as ZIP |
| `update_character_tags` | Update character tags |

**Object Management:**

| Tool | Description |
|---|---|
| `list_objects` | List your objects (paginated) |
| `get_object` | Get object details |
| `delete_object` | Delete an object |
| `update_object_tags` | Update object tags |

**Tile/Tileset Management:**

| Tool | Description |
|---|---|
| `list_tilesets` | List all tilesets |
| `get_tileset` | Get tileset details by UUID |
| `list_isometric_tiles` | List all isometric tiles |
| `get_isometric_tile` | Get isometric tile by UUID |
| `list_tiles_pro` | List all pro tiles |
| `get_tiles_pro` | Get pro tile by UUID |

### Account (1 tool)

| Tool | Description |
|---|---|
| `get_balance` | Show current API credit balance |

## Output

All generated images are saved to the `output_dir` specified in each tool call, with timestamped filenames.
Tools return the saved path(s) as text.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `PIXELLAB_SECRET` | Yes | API secret key (used as Bearer token) |

## Project structure

```
pixellab-mcp/
├── pyproject.toml
├── .env.example
└── pixellab_mcp/
    ├── server.py          # FastMCP server + tool registration
    ├── __main__.py        # python -m pixellab_mcp
    └── tools/
        ├── http_client.py # REST HTTP client (auth + async job polling)
        ├── image_utils.py # Image encoding/decoding helpers
        ├── generate.py    # Image generation tools
        ├── animate.py     # Animation tools
        ├── edit.py        # Editing tools
        ├── character.py   # Character + skeleton tools
        ├── rotate.py      # Rotation tools
        ├── tiles.py       # Tile/tileset tools
        ├── objects.py     # Map object tools
        └── management.py  # Character/object CRUD tools
```

## License

Private use. PixelLab API usage subject to [PixelLab Terms of Service](https://pixellab.ai).
