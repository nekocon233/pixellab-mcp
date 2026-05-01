"""Tools: animation generation."""
import json
from typing import Optional

from PIL import Image

from . import image_utils
from . import http_client


def register(mcp) -> None:

    # ── 1. Movement (walk/run/attack etc.) ────────────────────────────────────

    @mcp.tool()
    async def movement_generate(
        description: str,
        action: str,
        reference_image_path: str,
        output_dir: str,
        n_frames: int = 4,
        view: str = "low top-down",
        direction: str = "east",
        image_guidance_scale: float = 1.4,
        text_guidance_scale: float = 8.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
        mask_image_path: Optional[str] = None,
        inpainting_image_path: Optional[str] = None,
    ) -> str:
        """Animate a character with a movement action (walk, run, attack, etc.).

        Args:
            description: Character description e.g. "blue-robed mage".
            action: Animation action e.g. "walk", "run", "attack with sword".
            reference_image_path: Pixel art sprite to animate.
            n_frames: Number of animation frames (2-20).
            view: side / low top-down / high top-down
            direction: north / east / south / west
            init_image_path: Optional initial image for guided animation.
            mask_image_path: Inpainting mask (white = regenerate). Requires init_image_path and inpainting_image_path.
            inpainting_image_path: Image to inpaint over. Requires mask_image_path.
        """
        payload = {
            "description": description,
            "action": action,
            "reference_image": {"base64": image_utils.path_to_png_b64(reference_image_path), "type": "base64", "format": "png"},
            "image_size": {"width": 64, "height": 64},
            "n_frames": n_frames,
            "view": view,
            "direction": direction,
            "image_guidance_scale": image_guidance_scale,
            "text_guidance_scale": text_guidance_scale,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}
        if mask_image_path:
            payload["mask_image"] = {"base64": image_utils.path_to_png_b64(mask_image_path)}
        if inpainting_image_path:
            payload["inpainting_image"] = {"base64": image_utils.path_to_png_b64(inpainting_image_path)}

        result = await http_client.call("animate-with-text", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "movement", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 2. Animate with text v2 (Pro) ─────────────────────────────────────────

    @mcp.tool()
    async def animate_with_text(
        reference_image_path: str,
        action: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "none",
        direction: str = "none",
        no_background: bool = True,
        text_guidance_scale: float = 8.0,
        image_guidance_scale: float = 4.0,
        seed: int = 0,
    ) -> str:
        """Animate a pixel art character using a text action description (Pro quality).

        Args:
            reference_image_path: Character sprite to animate.
            action: Text description of animation e.g. "Walking", "Jump attack".
            view: side / low top-down / high top-down / none
            direction: north / east / south / west / none
            text_guidance_scale: How strongly to follow the text prompt.
            image_guidance_scale: How strongly to follow the reference image.
        """
        ref_b64 = image_utils.path_to_png_b64(reference_image_path)
        ref_img = Image.open(reference_image_path)
        rw, rh = ref_img.size
        payload = {
            "reference_image": {"base64": ref_b64, "type": "base64", "format": "png"},
            "reference_image_size": {"width": rw, "height": rh},
            "action": action,
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "text_guidance_scale": text_guidance_scale,
            "image_guidance_scale": image_guidance_scale,
            "seed": seed,
        }
        result = await http_client.call_async("animate-with-text-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "animate_text", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 3. Animate with text v3 ───────────────────────────────────────────────

    @mcp.tool()
    async def animate_with_text_v3(
        reference_image_path: str,
        action: str,
        output_dir: str,
        last_frame_path: Optional[str] = None,
        frame_count: int = 8,
        no_background: bool = False,
        seed: int = 0,
    ) -> str:
        """Animate a pixel art character with text (v3 - higher quality, even frame count).

        Args:
            reference_image_path: Character sprite (first frame).
            action: Text description of animation e.g. "Walking cycle".
            last_frame_path: Optional last frame for guided animation.
            frame_count: Number of frames; must be even, range 4-16.
            no_background: True = transparent background on generated frames.
        """
        ref_b64 = image_utils.path_to_png_b64(reference_image_path)
        ref_img = Image.open(reference_image_path)
        rw, rh = ref_img.size

        payload = {
            "first_frame": {"image": {"base64": ref_b64}, "size": {"width": rw, "height": rh}},
            "action": action,
            "frame_count": frame_count,
            "no_background": no_background,
            "seed": seed,
        }
        if last_frame_path:
            lf_b64 = image_utils.path_to_png_b64(last_frame_path)
            lf_img = Image.open(last_frame_path)
            lw, lh = lf_img.size
            payload["last_frame"] = {"image": {"base64": lf_b64}, "size": {"width": lw, "height": lh}}

        result = await http_client.call_async("animate-with-text-v3", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, rw, rh, "animate_text_v3", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 4. Animation from text ────────────────────────────────────────────────

    @mcp.tool()
    async def animation_generate(
        action: str,
        reference_image_path: str,
        output_dir: str,
        description: str = "",
        n_frames: int = 8,
        view: str = "low top-down",
        direction: str = "south",
        text_guidance_scale: float = 8.0,
        image_guidance_scale: float = 4.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
        init_image_strength: int = 300,
        mask_image_path: Optional[str] = None,
        inpainting_image_path: Optional[str] = None,
    ) -> str:
        """Generate an animation sequence from text and a reference character image.

        In V2, a reference character image is required (unlike the old template-based system).
        Use pixelart_flux_generate first if you need to create a character from scratch.

        Args:
            action: Animation type e.g. "walk", "run", "attack".
            reference_image_path: Character sprite to animate.
            description: Optional character description.
            n_frames: Number of frames to generate (2-20).
            init_image_path: Optional initial image for guided animation.
            mask_image_path: Inpainting mask (white = regenerate). Requires init_image_path and inpainting_image_path.
            inpainting_image_path: Image to inpaint over. Requires mask_image_path.
        """
        payload = {
            "description": description,
            "action": action,
            "reference_image": {"base64": image_utils.path_to_png_b64(reference_image_path), "type": "base64", "format": "png"},
            "image_size": {"width": 64, "height": 64},
            "n_frames": n_frames,
            "view": view,
            "direction": direction,
            "text_guidance_scale": text_guidance_scale,
            "image_guidance_scale": image_guidance_scale,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}
        if mask_image_path:
            payload["mask_image"] = {"base64": image_utils.path_to_png_b64(mask_image_path)}
        if inpainting_image_path:
            payload["inpainting_image"] = {"base64": image_utils.path_to_png_b64(inpainting_image_path)}

        result = await http_client.call("animate-with-text", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "animation", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 5. Interpolation ──────────────────────────────────────────────────────

    @mcp.tool()
    async def interpolation_generate(
        from_image_path: str,
        to_image_path: str,
        output_dir: str,
        action: str = "transforming",
        width: int = 64,
        height: int = 64,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Generate in-between frames interpolating from one sprite to another.

        Useful for morph animations, state transitions, death sequences etc.

        Args:
            from_image_path: Starting frame.
            to_image_path: Ending frame.
            action: Description of the transition e.g. "transforming", "dying".
        """
        from_b64 = image_utils.path_to_png_b64(from_image_path)
        from_img = Image.open(from_image_path)
        fw, fh = from_img.size

        to_b64 = image_utils.path_to_png_b64(to_image_path)
        to_img = Image.open(to_image_path)
        tw, th = to_img.size

        payload = {
            "start_image": {"image": {"base64": from_b64}, "size": {"width": fw, "height": fh}},
            "end_image": {"image": {"base64": to_b64}, "size": {"width": tw, "height": th}},
            "action": action,
            "image_size": {"width": width, "height": height},
            "no_background": no_background,
            "seed": seed,
        }
        result = await http_client.call_async("interpolation-v2", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "interpolation", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)
