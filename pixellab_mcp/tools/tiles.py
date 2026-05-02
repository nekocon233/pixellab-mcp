"""Tools: tile and tileset generation."""
from typing import List, Optional

from . import image_utils
from . import http_client


def register(mcp) -> None:

    # ── 1. Tileset (top-down, transition set) ────────────────────────────────

    @mcp.tool()
    async def tileset_generate(
        lower_description: str,
        upper_description: str,
        transition_description: str,
        output_dir: str,
        tile_width: int = 16,
        tile_height: int = 16,
        text_guidance_scale: float = 8.0,
        transition_size: float = 0.5,
        tileset_adherence: int = 100,
        tileset_adherence_freedom: float = 500.0,
        tile_strength: float = 1.0,
        outline: str = "",
        shading: str = "basic shading",
        detail: str = "low detail",
        view: str = "high top-down",
        seed: int = 0,
        lower_reference_path: Optional[str] = None,
        upper_reference_path: Optional[str] = None,
        transition_reference_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
        lower_base_tile_id: Optional[str] = None,
        upper_base_tile_id: Optional[str] = None,
    ) -> str:
        """Generate a complete tileset with lower, upper, and transition tiles (8-tile Wang set).

        Uses the modern POST /tilesets async endpoint. Retrieve result via get_tileset().

        Args:
            lower_description: Center/fill tile description e.g. "ocean".
            upper_description: Border/edge tile description e.g. "sand".
            transition_description: Transition tile description e.g. "rocks".
            tile_width/tile_height: Size of each tile (16 or 32 only).
            transition_size: 0 / 0.25 / 0.5 / 1.0.
            tileset_adherence: 0-500, how strictly to follow the tileset rules.
            tileset_adherence_freedom: 0-900, how flexible when following tileset structure.
            tile_strength: 0.1-2.0, pattern strength.
            lower_base_tile_id: Optional metadata ID for the lower base tile (for connected tilesets).
            upper_base_tile_id: Optional metadata ID for the upper base tile (for connected tilesets).
        """
        payload = {
            "lower_description": lower_description,
            "upper_description": upper_description,
            "transition_description": transition_description,
            "tile_size": {"width": tile_width, "height": tile_height},
            "text_guidance_scale": text_guidance_scale,
            "transition_size": transition_size,
            "tileset_adherence": tileset_adherence,
            "tileset_adherence_freedom": tileset_adherence_freedom,
            "tile_strength": tile_strength,
            "view": view,
            "seed": seed,
        }
        if outline:
            payload["outline"] = outline
        if shading:
            payload["shading"] = shading
        if detail:
            payload["detail"] = detail
        if lower_reference_path:
            payload["lower_reference_image"] = {"base64": image_utils.path_to_png_b64(lower_reference_path)}
        if upper_reference_path:
            payload["upper_reference_image"] = {"base64": image_utils.path_to_png_b64(upper_reference_path)}
        if transition_reference_path:
            payload["transition_reference_image"] = {"base64": image_utils.path_to_png_b64(transition_reference_path)}
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if lower_base_tile_id:
            payload["lower_base_tile_id"] = lower_base_tile_id
        if upper_base_tile_id:
            payload["upper_base_tile_id"] = upper_base_tile_id

        result = await http_client.call_async("tilesets", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(
            images, tile_width * 8, tile_height * 8, "tileset", output_dir
        )
        return f"Saved {len(paths)} tileset(s):\n" + "\n".join(paths)

    # ── 2. Tileset sidescroller ──────────────────────────────────────────────

    @mcp.tool()
    async def tileset_sidescroller_generate(
        lower_description: str,
        transition_description: str,
        output_dir: str,
        tile_width: int = 16,
        tile_height: int = 16,
        text_guidance_scale: float = 8.0,
        transition_size: float = 0.5,
        tileset_adherence: int = 100,
        tileset_adherence_freedom: float = 500.0,
        tile_strength: float = 1.0,
        outline: str = "",
        shading: str = "basic shading",
        detail: str = "low detail",
        seed: int = 0,
        lower_reference_path: Optional[str] = None,
        transition_reference_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
        lower_base_tile_id: Optional[str] = None,
    ) -> str:
        """Generate a side-scroller tileset with platform and transition tiles.

        Uses the modern POST /tilesets-sidescroller async endpoint. Retrieve result via get_tileset().

        Args:
            lower_description: Main platform tile e.g. "rocks".
            transition_description: Edge/transition tile e.g. "grass top".
            tile_width/tile_height: Individual tile dimensions (16 or 32).
            tileset_adherence: 0-500, how strictly to follow the tileset rules.
            tileset_adherence_freedom: 0-900, how flexible when following tileset structure.
            lower_base_tile_id: Optional metadata ID for the lower base tile (for connected tilesets).
        """
        payload = {
            "lower_description": lower_description,
            "transition_description": transition_description,
            "tile_size": {"width": tile_width, "height": tile_height},
            "text_guidance_scale": text_guidance_scale,
            "transition_size": transition_size,
            "tileset_adherence": tileset_adherence,
            "tileset_adherence_freedom": tileset_adherence_freedom,
            "tile_strength": tile_strength,
            "seed": seed,
        }
        if outline:
            payload["outline"] = outline
        if shading:
            payload["shading"] = shading
        if detail:
            payload["detail"] = detail
        if lower_reference_path:
            payload["lower_reference_image"] = {"base64": image_utils.path_to_png_b64(lower_reference_path)}
        if transition_reference_path:
            payload["transition_reference_image"] = {"base64": image_utils.path_to_png_b64(transition_reference_path)}
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if lower_base_tile_id:
            payload["lower_base_tile_id"] = lower_base_tile_id

        result = await http_client.call_async("tilesets-sidescroller", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(
            images, tile_width * 8, tile_height * 8, "tileset_side", output_dir
        )
        return f"Saved {len(paths)} tileset(s):\n" + "\n".join(paths)

    # ── 3. Tiles Pro ─────────────────────────────────────────────────────────

    @mcp.tool()
    async def tiles_pro_generate(
        description: str,
        output_dir: str,
        tile_type: str = "isometric",
        tile_size: int = 32,
        tile_height: int = 32,
        tile_view: str = "top-down",
        tile_view_angle: float = 20,
        tile_depth_ratio: float = 0.0,
        seed: int = 0,
        style_image_paths: Optional[List[str]] = None,
        style_color_palette: bool = True,
        style_outline: bool = True,
        style_detail: bool = True,
        style_shading: bool = True,
    ) -> str:
        """Generate professional-quality tiles including isometric, hex, octagon.

        Args:
            description: Numbered list e.g. "1). grass 2). dirt 3). stone".
            tile_type: isometric / hex / hex_pointy / octagon / square_topdown.
            tile_size: Tile size in pixels (16-256).
            tile_view: top-down / high top-down / low top-down / side.
            tile_view_angle: Viewing angle in degrees (0-90).
            tile_depth_ratio: Depth ratio (0-1).
            style_image_paths: Optional list of style reference images.
            style_color_palette: Include color palette in style matching.
            style_outline: Include outline in style matching.
            style_detail: Include detail in style matching.
            style_shading: Include shading in style matching.
        """
        payload = {
            "description": description,
            "tile_type": tile_type,
            "tile_size": tile_size,
            "tile_height": tile_height,
            "tile_view": tile_view,
            "tile_view_angle": tile_view_angle,
            "tile_depth_ratio": tile_depth_ratio,
            "seed": seed,
            "style_options": {
                "color_palette": style_color_palette,
                "outline": style_outline,
                "detail": style_detail,
                "shading": style_shading,
            },
        }
        if style_image_paths:
            from PIL import Image as _Image
            style_imgs = []
            for p in style_image_paths:
                img = _Image.open(p)
                w, h = img.size
                style_imgs.append({"image": {"base64": image_utils.path_to_png_b64(p)}, "size": {"width": w, "height": h}})
            payload["style_images"] = style_imgs

        result = await http_client.call_async("create-tiles-pro", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "tiles_pro", output_dir)
        return f"Saved {len(paths)} tile(s):\n" + "\n".join(paths)

    # ── 4. Isometric tile (NEW) ──────────────────────────────────────────────

    @mcp.tool()
    async def create_isometric_tile(
        description: str,
        output_dir: str,
        image_size: int = 64,
        isometric_tile_size: int = 32,
        isometric_tile_shape: str = "block",
        text_guidance_scale: float = 8.0,
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
    ) -> str:
        """Generate an isometric tile (NEW in V2).

        Args:
            description: Tile description e.g. "grass hill", "stone platform".
            image_size: Output image size in pixels (16-64).
            isometric_tile_size: Tile footprint size (16 or 32).
            isometric_tile_shape: thick tile / thin tile / block.
        """
        payload = {
            "description": description,
            "image_size": {"width": image_size, "height": image_size},
            "isometric_tile_size": isometric_tile_size,
            "isometric_tile_shape": isometric_tile_shape,
            "text_guidance_scale": text_guidance_scale,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        result = await http_client.call_async("create-isometric-tile", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, image_size, image_size, "iso_tile", output_dir)
        return f"Saved {len(paths)} tile(s):\n" + "\n".join(paths)
