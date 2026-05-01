"""Tools: image generation (text → pixel art)."""
import base64
import io
from typing import Optional

from PIL import Image

from . import image_utils
from . import http_client


def register(mcp) -> None:

    # ── 1. Pixelart Flux ──────────────────────────────────────────────────────

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
        isometric: bool = False,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate pixel art from text using the Pixflux model (general-purpose).

        Args:
            view: side / low top-down / high top-down / none
            direction: north / north-east / east / south-east / south / south-west / west / north-west / none
            outline: none / single color black outline / selective outline / lineless
            shading: none / basic shading / medium shading
            detail: low detail / medium detail / high detail
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
            "isometric": isometric,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        result = await http_client.call("create-image-pixflux", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pixelart_flux", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 2. Consistent-style (best style matching) ────────────────────────────

    @mcp.tool()
    async def consistent_style_generate(
        description: str,
        style_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        style_description: str = "",
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Generate pixel art frames that match the visual style of a reference image.

        This is the highest-quality style-matching tool.

        Args:
            description: What to generate, e.g. "warrior with sword".
            style_image_path: Local path to the style reference sprite (PNG).
            width: Output image width in pixels (max 512).
            height: Output image height in pixels.
            style_description: Additional style hints.
            no_background: True = transparent background.
            seed: 0 = random.
        """
        style_b64 = image_utils.path_to_png_b64(style_image_path)
        style_img = Image.open(style_image_path)
        sw, sh = style_img.size
        payload = {
            "style_images": [{"image": {"base64": style_b64}, "width": sw, "height": sh}],
            "description": description,
            "image_size": {"width": width, "height": height},
            "style_description": style_description,
            "no_background": no_background,
            "seed": seed,
        }
        result = await http_client.call_async("generate-with-style-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "consistent_style", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 3. Flux same-style (Bitforge) ────────────────────────────────────────

    @mcp.tool()
    async def pixflux_same_style_generate(
        description: str,
        style_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        text_guidance_scale: float = 8.0,
        style_strength: float = 50.0,
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
        """Generate a single pixel art image in the exact style of a reference, using the Bitforge model.

        Good for style-consistent single-frame assets.
        Max canvas: 200x200 pixels.

        Args:
            style_strength: 0-100, how strongly to match the style.
            view: side / low top-down / high top-down / none
            direction: north / east / south / west / none
            outline: e.g. "single color black outline" / "selective outline" / ""
            shading: e.g. "basic shading" / ""
            detail: e.g. "medium detail" / "low detail" / ""
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "style_image": {"base64": image_utils.path_to_png_b64(style_image_path)},
            "style_strength": style_strength,
            "view": view,
            "direction": direction,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "no_background": no_background,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        result = await http_client.call("create-image-bitforge", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "flux_same_style", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 4. Style-controlled generation (Bitforge) ────────────────────────────

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
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        coverage_percentage: float = 0.9,
        seed: int = 0,
        style_image_path: Optional[str] = None,
        style_strength: float = 50.0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
    ) -> str:
        """Generate pixel art with full style control using the Bitforge model.

        The most flexible single-image generation tool. Use style_image_path
        to apply a visual style transfer.

        Args:
            view: side / low top-down / high top-down
            direction: north / east / south / west / north-east / etc.
            outline: selective outline / single color black outline / lineless / none
            shading: none / basic shading / medium shading
            detail: low detail / medium detail / high detail
            coverage_percentage: how much of the canvas the subject fills (0-1)
            style_strength: 0-100, higher = more style influence
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
            "coverage_percentage": coverage_percentage,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if style_image_path:
            payload["style_image"] = {"base64": image_utils.path_to_png_b64(style_image_path)}
            payload["style_strength"] = style_strength
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        result = await http_client.call("create-image-bitforge", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "style", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 5. General images ────────────────────────────────────────────────────

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
            view: side / low top-down / high top-down / none
            direction: north / east / south / west / none
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        result = await http_client.call("create-image-pixflux", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "general", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 6. General XL (Pro generation) ───────────────────────────────────────

    @mcp.tool()
    async def general_xl_generate(
        description: str,
        output_dir: str,
        width: int = 128,
        height: int = 128,
        no_background: bool = False,
        seed: int = 0,
        style_image_path: Optional[str] = None,
        color_palette: bool = True,
        outline_style: bool = True,
        detail: bool = True,
        shading: bool = True,
    ) -> str:
        """Generate large-scale pixel art using the V2 Pro model (up to 792x688).

        Better for complex scenes. Supports style references.

        Args:
            color_palette: Match style color palette.
            outline_style: Match style outlines.
            detail: Match style detail level.
            shading: Match style shading.
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
            "seed": seed,
            "style_options": {
                "color_palette": color_palette,
                "outline": outline_style,
                "detail": detail,
                "shading": shading,
            },
        }
        if style_image_path:
            style_img = Image.open(style_image_path)
            sw, sh = style_img.size
            payload["style_image"] = {
                "image": {"base64": image_utils.path_to_png_b64(style_image_path)},
                "size": {"width": sw, "height": sh},
            }

        result = await http_client.call_async("generate-image-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "general_xl", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 7. Image → pixel art ─────────────────────────────────────────────────

    @mcp.tool()
    async def image_to_pixelart(
        image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        text_guidance_scale: float = 8.0,
        seed: int = 0,
    ) -> str:
        """Convert any photo or artwork to pixel art style.

        The input image is automatically cropped to match the output aspect ratio.

        Args:
            width/height: Output pixel art dimensions (16-320).
        """
        img = Image.open(image_path).convert("RGBA")
        ow, oh = img.size

        # Crop to output aspect ratio (centred)
        target_h = int(ow * height / width)
        if target_h > oh:
            target_w = int(oh * width / height)
            left = (ow - target_w) // 2
            img = img.crop((left, 0, left + target_w, oh))
        else:
            top = (oh - target_h) // 2
            img = img.crop((0, top, ow, top + target_h))

        # Downscale if over V2 limit (1280)
        cw, ch = img.size
        if max(cw, ch) > 1280:
            scale = 1280 / max(cw, ch)
            cw, ch = int(cw * scale), int(ch * scale)
        cw = max(16, (cw // 4) * 4)
        ch = max(16, (ch // 4) * 4)
        img = img.resize((cw, ch), Image.LANCZOS)

        # Encode as PNG base64
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        payload = {
            "image": {"base64": b64},
            "image_size": {"width": cw, "height": ch},
            "output_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "seed": seed,
        }
        result = await http_client.call("image-to-pixelart", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "to_pixelart", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)
