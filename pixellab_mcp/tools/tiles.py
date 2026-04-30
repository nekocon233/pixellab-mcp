"""Tools: tile and tileset generation."""
from typing import List, Optional

from . import image_utils
from . import ws_client


def register(mcp) -> None:

    # ── 1. Basic tiles ────────────────────────────────────────────────────────

    @mcp.tool()
    async def tiles_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "high top-down",
        text_guidance_scale: float = 8.0,
        init_image_strength: int = 300,
        negative_description: str = "mixels. amateur",
        seed: int = 0,
        reference_image_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate a seamlessly tileable pixel art tile from a text description.

        Args:
            description: Tile content e.g. "grass", "cobblestone road".
            view: high top-down / low top-down / side
            reference_image_path: Optional style reference image.
        """
        payload = {
            "description": description,
            "negative_description": negative_description,
            "image_size": {"width": width, "height": height},
            "view": view,
            "text_guidance_scale": text_guidance_scale,
            "init_image_strength": init_image_strength,
            "force_colors": False,
            "isometric": False,
            "oblique_projection": False,
            "seed": str(seed),
        }
        if reference_image_path:
            payload["reference_image"] = {"base64": image_utils.path_to_png_b64(reference_image_path)}
        payload["color_image"] = (
            {"base64": image_utils.path_to_png_b64(color_image_path)}
            if color_image_path
            else image_utils.blank_image_field()
        )
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        payload["model_name"] = "generate_tiles"
        result = await ws_client.call("generate-tiles", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "tiles", output_dir)
        return f"Saved {len(paths)} tile(s):\n" + "\n".join(paths)

    # ── 2. Tiles Pro ──────────────────────────────────────────────────────────

    @mcp.tool()
    async def tiles_pro_generate(
        description: str,
        output_dir: str,
        tile_type: str = "isometric",
        tile_size: str = "32",
        tile_view_angle: int = 20,
        thickness: int = 30,
        method: str = "description",
        seed: int = 0,
        style_image_paths: Optional[List[str]] = None,
    ) -> str:
        """Generate professional-quality tiles including isometric tiles.

        Args:
            description: Numbered list of tile descriptions e.g. "1). grass 2). dirt 3). stone".
            tile_type: isometric / flat / etc.
            tile_size: "16", "32", "64"
            tile_view_angle: Viewing angle in degrees (0–90).
            thickness: Block thickness for isometric tiles (0–100).
            method: "description" = text-guided.
            style_image_paths: Optional list of style reference images.
        """
        payload = {
            "description": description,
            "tile_type": tile_type,
            "tile_size": tile_size,
            "tile_view_angle": tile_view_angle,
            "thickness": thickness,
            "method": method,
            "seed": str(seed),
            "style_options": {
                "color_palette": True,
                "outline": True,
                "detail": True,
                "shading": True,
            },
        }
        if style_image_paths:
            payload["style_images_display"] = [
                image_utils.path_to_png_b64(p) for p in style_image_paths
            ]

        payload["model_name"] = "generate_tiles_pro"
        result = await ws_client.call("generate-tiles-pro", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "tiles_pro", output_dir)
        return f"Saved {len(paths)} tile(s):\n" + "\n".join(paths)

    # ── 3. Tiles style ────────────────────────────────────────────────────────

    @mcp.tool()
    async def tiles_style_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "high top-down",
        text_guidance_scale: float = 8.0,
        style_guidance_scale: float = 1.0,
        map_zoom: str = "16x16",
        init_image_strength: int = 300,
        negative_description: str = "mixels. amateur",
        seed: int = 0,
        style_image_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate a tileable map tile with a specific visual style from a reference image.

        Args:
            description: Tile content e.g. "forest floor with roots".
            style_image_path: Style reference pixel art image.
            style_guidance_scale: How closely to match the style (0.5–3.0).
            map_zoom: Pixel scale e.g. "16x16", "32x32".
        """
        payload = {
            "description": description,
            "negative_description": negative_description,
            "image_size": {"width": width, "height": height},
            "view": view,
            "text_guidance_scale": text_guidance_scale,
            "style_guidance_scale": style_guidance_scale,
            "map_tile": True,
            "map_zoom": map_zoom,
            "init_image_strength": init_image_strength,
            "force_colors": False,
            "isometric": False,
            "oblique_projection": False,
            "seed": str(seed),
        }
        if style_image_path:
            payload["style_image"] = {"base64": image_utils.path_to_png_b64(style_image_path)}
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        payload["model_name"] = "generate_tiles_style"
        result = await ws_client.call("generate-tiles-style", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "tiles_style", output_dir)
        return f"Saved {len(paths)} tile(s):\n" + "\n".join(paths)

    # ── 4. Tileset (transition set) ───────────────────────────────────────────

    @mcp.tool()
    async def tileset_generate(
        inner_description: str,
        outer_description: str,
        transition_description: str,
        output_dir: str,
        tile_width: int = 16,
        tile_height: int = 16,
        text_guidance_scale: float = 8.0,
        transition_size: float = 0.5,
        tileset_adherence: int = 100,
        tileset_type: str = "higher_lower",
        outline: str = "",
        shading: str = "basic shading",
        detail: str = "low detail",
        seed: int = 0,
        inner_reference_path: Optional[str] = None,
        outer_reference_path: Optional[str] = None,
        transition_reference_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a complete tileset with inner, outer, and transition tiles (8-tile Wang set).

        The output canvas is automatically sized to tile_size × 8.

        Args:
            inner_description: Center/fill tile description e.g. "ocean".
            outer_description: Border/edge tile description e.g. "sand".
            transition_description: Transition tile description e.g. "rocks".
            tile_width/tile_height: Size of each individual tile.
            transition_size: Proportion of transition area (0–1).
            tileset_type: higher_lower / other types.
        """
        payload = {
            "inner_description": inner_description,
            "outer_description": outer_description,
            "transition_description": transition_description,
            "image_size": {"width": tile_width * 8, "height": tile_height},
            "reference_image_size": {"width": tile_width, "height": tile_height},
            "text_guidance_scale": text_guidance_scale,
            "transition_size": transition_size,
            "tileset_adherence": tileset_adherence,
            "tileset_adherence_freedom": 500,
            "tileset_type": tileset_type,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "seed": str(seed),
        }
        if inner_reference_path:
            payload["inner_reference_image"] = {"base64": image_utils.path_to_png_b64(inner_reference_path)}
        if outer_reference_path:
            payload["outer_reference_image"] = {"base64": image_utils.path_to_png_b64(outer_reference_path)}
        if transition_reference_path:
            payload["transition_reference_image"] = {"base64": image_utils.path_to_png_b64(transition_reference_path)}
        payload["color_image"] = (
            {"base64": image_utils.path_to_png_b64(color_image_path)}
            if color_image_path
            else image_utils.blank_image_field()
        )

        payload["model_name"] = "generate_tileset"
        result = await ws_client.call("generate-tileset", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(
            images, tile_width * 8, tile_height, "tileset", output_dir
        )
        return f"Saved {len(paths)} tileset(s):\n" + "\n".join(paths)

    # ── 5. Tileset sidescroller ───────────────────────────────────────────────

    @mcp.tool()
    async def tileset_sidescroller_generate(
        inner_description: str,
        transition_description: str,
        output_dir: str,
        tile_width: int = 16,
        tile_height: int = 16,
        text_guidance_scale: float = 8.0,
        transition_size: float = 0.5,
        tileset_adherence: int = 100,
        outline: str = "",
        shading: str = "basic shading",
        detail: str = "low detail",
        seed: int = 0,
        inner_reference_path: Optional[str] = None,
        transition_reference_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a side-scroller tileset with platform and transition tiles.

        Args:
            inner_description: Main platform tile e.g. "rocks".
            transition_description: Edge/transition tile e.g. "grass top".
            tile_width/tile_height: Individual tile dimensions.
        """
        payload = {
            "inner_description": inner_description,
            "transition_description": transition_description,
            "image_size": {"width": tile_width * 8, "height": tile_height},
            "reference_image_size": {"width": tile_width, "height": tile_height},
            "text_guidance_scale": text_guidance_scale,
            "transition_size": transition_size,
            "tileset_adherence": tileset_adherence,
            "tileset_adherence_freedom": 500,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "seed": str(seed),
        }
        if inner_reference_path:
            payload["inner_reference_image"] = {"base64": image_utils.path_to_png_b64(inner_reference_path)}
        if transition_reference_path:
            payload["transition_reference_image"] = {"base64": image_utils.path_to_png_b64(transition_reference_path)}
        payload["color_image"] = (
            {"base64": image_utils.path_to_png_b64(color_image_path)}
            if color_image_path
            else image_utils.blank_image_field()
        )

        payload["model_name"] = "generate_tileset_sidescroller"
        result = await ws_client.call("generate-tileset-sidescroller", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(
            images, tile_width * 8, tile_height, "tileset_side", output_dir
        )
        return f"Saved {len(paths)} tileset(s):\n" + "\n".join(paths)

    # ── 6. Texture ────────────────────────────────────────────────────────────

    @mcp.tool()
    async def texture_generate(
        description: str,
        output_dir: str,
        width: int = 16,
        height: int = 16,
        text_guidance_scale: float = 8.0,
        texture_strength: float = 1.0,
        shading: str = "basic shading",
        detail: str = "low detail",
        init_image_strength: int = 150,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate a seamless texture pattern (good for small repeating tiles).

        Args:
            description: Texture description e.g. "ocean water", "brick wall", "dirt".
            texture_strength: Pattern strength 0–2; higher = more repetitive texture.
            shading: none / basic shading / medium shading
            detail: low detail / medium detail / high detail
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "texture_strength": texture_strength,
            "shading": shading,
            "detail": detail,
            "init_image_strength": init_image_strength,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        payload["model_name"] = "generate_texture"
        result = await ws_client.call("generate-texture", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "texture", output_dir)
        return f"Saved {len(paths)} texture(s):\n" + "\n".join(paths)
