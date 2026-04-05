"""Tools: sprite rotation / view-change."""
from typing import List, Optional

from . import image_utils
from . import ws_client


def register(mcp) -> None:

    # ── 1. Single rotation ───────────────────────────────────────────────────

    @mcp.tool()
    async def rotate_single(
        from_image_path: str,
        width: int = 64,
        height: int = 64,
        view_change: int = 0,
        direction_change: int = 45,
        image_guidance_scale: float = 3.0,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Rotate a sprite by a specific view/direction offset.

        Valid sizes: 16, 32, 64, 128 (powers of two only).

        Args:
            from_image_path: Source sprite to rotate.
            view_change: Vertical tilt change in degrees (e.g. 0).
            direction_change: Horizontal rotation in degrees (e.g. 45, 90, 135, -45).
            image_guidance_scale: How closely to follow the source image (1–10).
        """
        payload = {
            "from_image": image_utils.path_to_png_b64(from_image_path),
            "image_size": {"width": width, "height": height},
            "view_change": str(view_change),
            "direction_change": str(direction_change),
            "image_guidance_scale": image_guidance_scale,
            "init_image_strength": init_image_strength,
            "use_inpainting": False,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)

        result = await ws_client.call("generate-rotate-single", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "rotate_single")
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 2. Multi-direction rotations ─────────────────────────────────────────

    @mcp.tool()
    async def rotations_generate(
        rotation_image_paths: List[str],
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        image_guidance_scale: float = 2.0,
        text_guidance_scale: float = 8.0,
        init_image_strength: int = 300,
        forced_symmetry: bool = False,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate all cardinal rotations (S/E/N/W) for a character from existing views.

        Provide paths to existing direction images in rotation_image_paths
        (order: South, East, North, West).  Missing views are generated.

        Args:
            rotation_image_paths: List of 1–4 paths to existing direction frames.
            view: low top-down / high top-down / side
            forced_symmetry: Mirror-copy left↔right symmetrical directions.
        """
        rotation_images = [image_utils.path_to_png_b64(p) for p in rotation_image_paths]
        payload = {
            "rotation_images": rotation_images,
            "image_size": {"width": width, "height": height},
            "view": view,
            "image_guidance_scale": image_guidance_scale,
            "text_guidance_scale": text_guidance_scale,
            "init_image_strength": init_image_strength,
            "forced_symmetry": forced_symmetry,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)

        result = await ws_client.call("generate-rotations", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "rotations")
        return f"Saved {len(paths)} rotation(s):\n" + "\n".join(paths)

    # ── 3. Generate 4 rotations from text ────────────────────────────────────

    @mcp.tool()
    async def four_rotations_generate(
        description: str,
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
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate 4 directional frames (N/E/S/W) for a new character from text.

        Args:
            template_name: female-humanoid / male-humanoid / etc.
            ai_freedom: 0 = template-strict; higher = more creative
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
            "n_rows": 4,
            "n_columns": 1,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)

        result = await ws_client.call("generate-4-rotations", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "4_rotations")
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 4. Generate 8 rotations from text ────────────────────────────────────

    @mcp.tool()
    async def eight_rotations_generate(
        description: str,
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
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate 8 directional frames (all eight compass directions) for a new character from text.

        Args:
            template_name: female-humanoid / male-humanoid / etc.
            ai_freedom: 0 = template-strict; higher = more creative
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
            "n_rows": 1,
            "n_columns": 8,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)

        result = await ws_client.call("generate-8-rotations", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "8_rotations")
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 5. Reference → 8 rotations ───────────────────────────────────────────

    @mcp.tool()
    async def reference_to_8_rotations(
        description: str,
        concept_image_path: str,
        reference_image_path: str,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        style_description: str = "",
        method: str = "create_with_style",
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Generate all 8 compass-direction rotations from a concept + style reference image.

        Args:
            concept_image_path: Sketch or concept art showing the character shape.
            reference_image_path: Style reference pixel art image.
            method: create_with_style / other
        """
        payload = {
            "description": description,
            "style_description": style_description,
            "display_concept_image": image_utils.path_to_png_b64(concept_image_path),
            "display_reference_image": image_utils.path_to_png_b64(reference_image_path),
            "image_size": {"width": width, "height": height},
            "view": view,
            "method": method,
            "no_background": no_background,
            "seed": str(seed),
        }
        result = await ws_client.call("generate-reference-to-8-rotations", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "ref_to_8rot")
        return f"Saved {len(paths)} rotation(s):\n" + "\n".join(paths)
