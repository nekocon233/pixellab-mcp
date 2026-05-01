"""Tools: image generation (text → pixel art)."""
import base64
import io
from typing import List, Optional

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
        background_removal_task: str = "remove_simple_background",
        text_guidance_scale: float = 8.0,
        outline: str = "single color black outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        isometric: bool = False,
        oblique_projection: bool = False,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        mask_image_path: Optional[str] = None,
    ) -> str:
        """Generate pixel art from text using the Pixflux model (general-purpose).

        Args:
            view: side / low top-down / high top-down / none
            direction: north / north-east / east / south-east / south / south-west / west / north-west / none
            no_background: Generate with transparent background.
            background_removal_task: "remove_simple_background" (faster) or "remove_complex_background" (handles complex edges).
            outline: none / single color black outline / selective outline / lineless
            shading: none / basic shading / medium shading
            detail: low detail / medium detail / high detail
            isometric: true = isometric projection
            oblique_projection: true = oblique projection
            mask_image_path: Inpainting mask (white = regenerate). Requires init_image_path.
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "background_removal_task": background_removal_task,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "isometric": isometric,
            "oblique_projection": oblique_projection,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}
        if mask_image_path:
            payload["mask_image"] = {"base64": image_utils.path_to_png_b64(mask_image_path)}

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
        extra_style_image_paths: str = "",
    ) -> str:
        """Generate pixel art frames that match the visual style of reference image(s).

        This is the highest-quality style-matching tool. Supports 1–4 style reference images.

        Args:
            description: What to generate, e.g. "warrior with sword".
            style_image_path: Local path to the primary style reference sprite (PNG).
            width: Output image width in pixels (max 512).
            height: Output image height in pixels.
            style_description: Additional style hints.
            no_background: True = transparent background.
            seed: 0 = random.
            extra_style_image_paths: JSON list of additional style image paths (up to 3 more, 4 total).
        """
        style_images = []
        # Primary style image
        style_b64 = image_utils.path_to_png_b64(style_image_path)
        style_img = Image.open(style_image_path)
        sw, sh = style_img.size
        style_images.append({"image": {"base64": style_b64}, "size": {"width": sw, "height": sh}})

        # Additional style images (up to 3 more, 4 total)
        if extra_style_image_paths:
            import json
            extra_paths = json.loads(extra_style_image_paths)
            for p in extra_paths[:3]:
                b64 = image_utils.path_to_png_b64(p)
                img = Image.open(p)
                w, h = img.size
                style_images.append({"image": {"base64": b64}, "size": {"width": w, "height": h}})

        payload = {
            "style_images": style_images,
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
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

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
        isometric: bool = False,
        oblique_projection: bool = False,
        coverage_percentage: float = 0.9,
        seed: int = 0,
        style_image_path: Optional[str] = None,
        style_strength: float = 50.0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
        mask_image_path: Optional[str] = None,
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
            isometric: True = isometric projection
            oblique_projection: True = oblique projection
            coverage_percentage: how much of the canvas the subject fills (0-1)
            style_strength: 0-100, higher = more style influence
            mask_image_path: Inpainting mask (white = regenerate). Requires init_image_path.
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
            "oblique_projection": oblique_projection,
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
        if mask_image_path:
            payload["mask_image"] = {"base64": image_utils.path_to_png_b64(mask_image_path)}

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
        reference_image_paths: Optional[List[str]] = None,
        color_image_path: Optional[str] = None,
        color_palette: bool = True,
        outline_style: bool = True,
        detail: bool = True,
        shading: bool = True,
    ) -> str:
        """Generate large-scale pixel art using the V2 Pro model (up to 792x688).

        Better for complex scenes. Supports style references and up to 4 reference images.

        Args:
            color_palette: Match style color palette.
            outline_style: Match style outlines.
            detail: Match style detail level.
            shading: Match style shading.
            reference_image_paths: Up to 4 image paths for subject guidance.
            color_image_path: Optional color palette reference image.
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
        if reference_image_paths:
            ref_images = []
            for rp in reference_image_paths[:4]:
                rimg = Image.open(rp)
                rw, rh = rimg.size
                ref_images.append({
                    "image": {"base64": image_utils.path_to_png_b64(rp)},
                    "size": {"width": rw, "height": rh},
                })
            payload["reference_images"] = ref_images
        if style_image_path:
            style_img = Image.open(style_image_path)
            sw, sh = style_img.size
            payload["style_image"] = {
                "image": {"base64": image_utils.path_to_png_b64(style_image_path)},
                "size": {"width": sw, "height": sh},
            }
        if color_image_path is not None:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

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

    # ── 8. Pixen model ───────────────────────────────────────────────────────

    @mcp.tool()
    async def pixen_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "side",
        direction: str = "south",
        no_background: bool = True,
        negative_description: str = "",
        text_guidance_scale: float = 8.0,
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        isometric: bool = False,
        oblique_projection: bool = False,
        background_removal_task: str = "remove_simple_background",
        style_strength: float = 50.0,
        coverage_percentage: float = 0.9,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        style_image_path: Optional[str] = None,
        mask_image_path: Optional[str] = None,
        inpainting_image_path: Optional[str] = None,
        skeleton_keypoints: Optional[str] = None,
        skeleton_guidance_scale: float = 1.0,
    ) -> str:
        """Generate pixel art using the Pixen model.

        Pixen is a dedicated pixel art model optimised for small sprites (max 768x768, max area 512x512).

        Args:
            view: side / low top-down / high top-down / none
            direction: north / north-east / east / south-east / south / south-west / west / north-west / none
            negative_description: Text description of what to avoid in the generated image.
            outline: none / single color black outline / selective outline / lineless
            shading: none / basic shading / medium shading
            detail: low detail / medium detail / high detail
            isometric: True = isometric projection
            oblique_projection: True = oblique projection
            background_removal_task: remove_simple_background / remove_complex_background
            style_strength: 0-100, how strongly to apply style from style_image_path.
            coverage_percentage: 0-1, how much of the canvas the subject fills.
            mask_image_path: Inpainting mask (white = regenerate). Requires inpainting_image_path and init_image_path.
            inpainting_image_path: Image to inpaint over. Requires mask_image_path.
            skeleton_keypoints: JSON array of keypoint objects to control character pose.
                Each keypoint: {"x": 0.5, "y": 0.3, "label": "NOSE", "z_index": 0}.
            skeleton_guidance_scale: How strictly to follow the skeleton (0-5).
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
            "oblique_projection": oblique_projection,
            "background_removal_task": background_removal_task,
            "style_strength": style_strength,
            "coverage_percentage": coverage_percentage,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if negative_description:
            payload["negative_description"] = negative_description
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}
        if style_image_path:
            payload["style_image"] = {"base64": image_utils.path_to_png_b64(style_image_path)}
        if mask_image_path:
            payload["mask_image"] = {"base64": image_utils.path_to_png_b64(mask_image_path)}
        if inpainting_image_path:
            payload["inpainting_image"] = {"base64": image_utils.path_to_png_b64(inpainting_image_path)}
        if skeleton_keypoints:
            import json as _json
            payload["skeleton_keypoints"] = _json.loads(skeleton_keypoints)
            payload["skeleton_guidance_scale"] = skeleton_guidance_scale

        result = await http_client.call("create-image-pixen", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pixen", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 9. Generate UI element ───────────────────────────────────────────────

    @mcp.tool()
    async def generate_ui_element(
        description: str,
        output_dir: str,
        width: int = 256,
        height: int = 256,
        no_background: bool = True,
        seed: int = 0,
        concept_image_path: Optional[str] = None,
        color_palette: Optional[str] = None,
    ) -> str:
        """Generate a pixel art UI element (button, health bar, icon, frame, etc.).

        Uses the Pro model (generate-ui-v2) designed specifically for UI assets.

        Args:
            description: UI element description e.g. "medieval stone button", "sci-fi health bar".
            width: Canvas width (16-792).
            height: Canvas height (16-688).
            no_background: True = transparent background.
            concept_image_path: Optional concept image to guide the design.
            color_palette: Optional color palette hint e.g. "brown and gold", "blue and silver".
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
            "seed": seed,
        }
        if concept_image_path:
            payload["concept_image"] = {"base64": image_utils.path_to_png_b64(concept_image_path)}
        if color_palette:
            payload["color_palette"] = color_palette

        result = await http_client.call_async("generate-ui-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "ui_element", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)
