"""Tools: map object and multi-direction object generation."""
from typing import Optional

from . import image_utils
from . import http_client


def register(mcp) -> None:

    # ── 1. Create map object ─────────────────────────────────────────────────

    @mcp.tool()
    async def create_map_object(
        description: str,
        output_dir: str,
        width: int = 128,
        height: int = 128,
        view: str = "high top-down",
        text_guidance_scale: float = 8.0,
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        no_background: bool = True,
        seed: int = 0,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a map object (tree, rock, chest, etc.) for top-down games.

        Args:
            description: Object description e.g. "oak tree", "treasure chest", "stone wall".
            width/height: Image size (32-400).
            view: low top-down / high top-down / side.
            no_background: True = transparent background.
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "view": view,
            "text_guidance_scale": text_guidance_scale,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "no_background": no_background,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call_async("map-objects", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "map_object", output_dir)
        return f"Saved {len(paths)} object(s):\n" + "\n".join(paths)

    # ── 2. Create object with 4 directions ───────────────────────────────────

    @mcp.tool()
    async def create_object_4_directions(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        text_guidance_scale: float = 8.0,
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate an object with 4 directional views (N/E/S/W).

        Good for items, props, or simple objects that need to face different directions.

        Args:
            description: Object description e.g. "wooden barrel", "flag pole".
            width/height: Image size (32-256).
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "view": view,
            "text_guidance_scale": text_guidance_scale,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call_async("create-object-with-4-directions", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "obj_4dir", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)
