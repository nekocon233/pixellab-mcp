"""Tools: utility operations (Canny edge, correct, etc.)."""
from typing import Optional

from . import image_utils
from . import ws_client


def register(mcp) -> None:

    # ── 1. Canny edge-guided generation ──────────────────────────────────────

    @mcp.tool()
    async def canny_generate(
        canny_image_path: str,
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "side",
        direction: str = "south",
        text_guidance_scale: float = 8.0,
        canny_guidance_scale: float = 1.0,
        no_background: bool = False,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
    ) -> str:
        """Generate pixel art guided by a Canny edge map for precise shape control.

        Args:
            canny_image_path: Edge-detected image (black background, white edges).
            description: What to generate following the edge shape.
            canny_guidance_scale: How strictly to follow the edge map (0.5 = loose, 2 = strict).
            view: side / low top-down / high top-down
            direction: north / east / south / west
        """
        payload = {
            "canny_image": image_utils.path_to_png_b64(canny_image_path),
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "canny_guidance_scale": canny_guidance_scale,
            "view": view,
            "direction": direction,
            "view_direction": False,
            "view_direction_guidance_scale": 4,
            "pixelart_style_guidance_scale": 4,
            "no_background": no_background,
            "no_background_guidance_scale": 4,
            "init_image_strength": init_image_strength,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)

        result = await ws_client.call("generate-general-canny", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "canny", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)
