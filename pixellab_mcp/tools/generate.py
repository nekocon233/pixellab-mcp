"""Tools: image generation (text → pixel art)."""
from typing import Optional

from . import image_utils
from . import ws_client


def register(mcp) -> None:

    # ── 1. Consistent-style (best style matching, RGBA encoding) ─────────────

    @mcp.tool()
    async def consistent_style_generate(
        description: str,
        style_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        style_description: str = "",
        no_background: bool = True,
        output_format: str = "frames",
        seed: int = 0,
    ) -> str:
        """Generate pixel art frames that match the visual style of a reference image.

        This is the highest-quality style-matching tool – equivalent to Aseprite's
        "Create images from style references" (Pro) feature.  The reference image is
        encoded as raw RGBA for maximum fidelity.

        Frame count depends on sprite size (tier-1 limits):
          ≤32 px  → up to 64 frames
          33-64 px → up to 16 frames
          65-128 px → up to 4 frames

        Args:
            description: What to generate, e.g. "warrior with sword".
            style_image_path: Local path to the style reference sprite (RGBA PNG).
            width: Output image width in pixels (max 512 for tier-2).
            height: Output image height in pixels.
            style_description: Additional style hints.
            no_background: True = transparent background.
            output_format: "frames" returns all generated frames.
            seed: 0 = random.
        """
        b64, w, h = image_utils.path_to_rgba_b64(style_image_path)
        payload = {
            "description": description,
            "style_description": style_description,
            "style_images": [{"base64": b64, "width": w, "height": h}],
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
            "output_format": output_format,
            "seed": seed,
        }
        result = await ws_client.call("generate-consistent-style", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "consistent_style", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 2. Flux same-style ────────────────────────────────────────────────────

    @mcp.tool()
    async def pixflux_same_style_generate(
        description: str,
        style_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        text_guidance_scale: float = 8.0,
        no_background: bool = True,
        view: str = "none",
        direction: str = "none",
        outline: str = "",
        shading: str = "",
        detail: str = "",
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate a single pixel art image in the exact style of a reference, using the Flux model.

        Good for style-consistent single-frame assets.
        Max canvas: 128×128 pixels (area ≤ 128*128).

        Args:
            view: side / low top-down / high top-down / none
            direction: north / east / south / west / none
            outline: e.g. "single color black outline" / "selective outline" / ""
            shading: e.g. "basic shading" / ""
            detail: e.g. "medium detail" / "low detail" / ""
        """
        payload = {
            "description": description,
            "style_image": image_utils.path_to_png_b64(style_image_path),
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "no_background": no_background,
            "view": view,
            "direction": direction,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "seed": seed,
            "isometric": False,
            "oblique_projection": False,
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)
            payload["init_image_strength"] = init_image_strength

        result = await ws_client.call("generate-flux-same-style", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "flux_same_style", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 3. Pixelart Flux ──────────────────────────────────────────────────────

    @mcp.tool()
    async def pixelart_flux_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "side",
        direction: str = "south",
        no_background: bool = True,
        text_guidance_scale: float = 8.0,
        outline: str = "single color black outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        map_tile: bool = False,
        isometric: bool = False,
        init_image_strength: int = 150,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate pixel art from text using the Pixelart Flux model (general-purpose).

        Args:
            view: side / low top-down / high top-down / none
            direction: north / north-east / east / south-east / south / south-west / west / north-west / none
            outline: none / single color black outline / selective outline / lineless
            shading: none / basic shading / medium shading
            detail: low detail / medium detail / high detail
            map_tile: true = tileable map tile output
            isometric: true = isometric projection
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "seed": seed,
            "map_tile": map_tile,
            "isometric": isometric,
            "oblique_projection": False,
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)
            payload["init_image_strength"] = init_image_strength

        result = await ws_client.call("generate-pixelart-flux", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pixelart_flux", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 4. Style-controlled generation ───────────────────────────────────────

    @mcp.tool()
    async def style_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "side",
        direction: str = "south",
        no_background: bool = True,
        text_guidance_scale: float = 8.0,
        negative_description: str = "",
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        coverage_percentage: float = 0.9,
        seed: int = 0,
        reference_image_path: Optional[str] = None,
        style_image_path: Optional[str] = None,
        style_strength: float = 0.0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
    ) -> str:
        """Generate pixel art with full style control: reference poses, style images, palettes.

        The most flexible single-image generation tool.  Use reference_image_path
        to provide a pose/composition reference.  style_image_path + style_strength
        applies a visual style transfer on top.

        Args:
            view: side / low top-down / high top-down
            direction: north / east / south / west / north-east / etc.
            outline: selective outline / single color black outline / lineless / none
            shading: none / basic shading / medium shading
            detail: low detail / medium detail / high detail
            coverage_percentage: how much of the canvas the subject fills (0–1)
            style_strength: 0 = ignore style image; higher = more influence
        """
        payload = {
            "description": description,
            "negative_description": negative_description,
            "text_guidance_scale": text_guidance_scale,
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "coverage_percentage": coverage_percentage,
            "seed": seed,
            "map_tile": False,
            "force_colors": False,
            "isometric": False,
            "oblique_projection": False,
        }
        if reference_image_path:
            payload["reference_image"] = image_utils.path_to_png_b64(reference_image_path)
        if style_image_path:
            payload["style_image"] = image_utils.path_to_png_b64(style_image_path)
            payload["style_strength"] = style_strength
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)
            payload["init_image_strength"] = init_image_strength

        result = await ws_client.call("generate-style", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "style", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 5. Spritesheet (instant character) ───────────────────────────────────

    @mcp.tool()
    async def spritesheet_generate(
        description: str,
        output_dir: str,
        width: int = 32,
        height: int = 32,
        view: str = "side",
        text_guidance_scale: float = 8.0,
        template_name: str = "female-humanoid",
        category: str = "realistic",
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        ai_freedom: int = 0,
        n_rows: int = 4,
        n_columns: int = 4,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a full character spritesheet with multiple animation frames.

        n_rows × n_columns determines the grid layout of the output sheet.
        ai_freedom=0 strictly follows the template; higher values allow more creative freedom.

        Args:
            template_name: female-humanoid / male-humanoid / etc.
            category: realistic / cartoon / etc.
            ai_freedom: 0 = strict template adherence; 750+ = very free
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "template_name": template_name,
            "category": category,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "ai_freedom": ai_freedom,
            "n_rows": n_rows,
            "n_columns": n_columns,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)

        result = await ws_client.call("generate-spritesheet", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(
            images, width * n_columns, height * n_rows, "spritesheet", output_dir
        )
        return f"Saved {len(paths)} spritesheet(s):\n" + "\n".join(paths)

    # ── 6. General images ─────────────────────────────────────────────────────

    @mcp.tool()
    async def general_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "high top-down",
        direction: str = "none",
        no_background: bool = False,
        text_guidance_scale: float = 8.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
    ) -> str:
        """Generate general pixel art: scenes, backgrounds, objects (not character-focused).

        Args:
            view: side / low top-down / high top-down
            direction: north / east / south / west / none
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "view_direction": False,
            "view_direction_guidance_scale": 8,
            "pixelart_style_guidance_scale": 4,
            "no_background_guidance_scale": 4,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)
            payload["init_image_strength"] = init_image_strength

        result = await ws_client.call("generate-general", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "general", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 7. General XL ─────────────────────────────────────────────────────────

    @mcp.tool()
    async def general_xl_generate(
        description: str,
        output_dir: str,
        width: int = 128,
        height: int = 128,
        view: str = "none",
        direction: str = "none",
        no_background: bool = False,
        negative_description: str = "",
        guidance_scale: float = 8.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
    ) -> str:
        """Generate large-scale pixel art using the XL model. Better for complex scenes."""
        payload = {
            "description": description,
            "negative_description": negative_description,
            "image_size": {"width": width, "height": height},
            "guidance_scale": guidance_scale,
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "view_direction": False,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)
            payload["init_image_strength"] = init_image_strength

        result = await ws_client.call("generate-general-xl", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "general_xl", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 8. Image → pixel art ──────────────────────────────────────────────────

    @mcp.tool()
    async def image_to_pixelart(
        image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        text_guidance_scale: float = 8.0,
        no_background: bool = False,
        seed: int = 0,
    ) -> str:
        """Convert any photo or artwork to pixel art style."""
        payload = {
            "image": image_utils.path_to_png_b64(image_path),
            "image_size": {"width": width, "height": height},
            "width": width,
            "height": height,
            "text_guidance_scale": text_guidance_scale,
            "no_background": no_background,
            "seed": seed,
        }
        result = await ws_client.call("generate-image-to-pixelart", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "to_pixelart", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)
