"""Tools: animation generation."""
from typing import List, Optional

from . import image_utils
from . import ws_client


def register(mcp) -> None:

    # ── 1. Movement (walk/run/attack etc.) ────────────────────────────────────

    @mcp.tool()
    async def movement_generate(
        description: str,
        action: str,
        reference_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        n_frames: int = 4,
        view: str = "low top-down",
        direction: str = "east",
        image_guidance_scale: float = 1.4,
        text_guidance_scale: float = 8.0,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Animate a character with a movement action (walk, run, attack, etc.).

        Args:
            description: Character description e.g. "blue-robed mage".
            action: Animation action e.g. "walk", "run", "attack with sword".
            reference_image_path: Pixel art sprite to animate.
            n_frames: Number of animation frames (2–20).
            view: side / low top-down / high top-down
            direction: north / east / south / west
        """
        payload = {
            "character": description,
            "action": action,
            "movement_images": [{"base64": image_utils.path_to_png_b64(reference_image_path)}],
            "inpainting_images": ["none", "none", "none", "none"],
            "selected_reference_image": {"base64": image_utils.path_to_png_b64(reference_image_path)},
            "image_size": {"width": width, "height": height},
            "n_frames": n_frames,
            "view": view,
            "direction": direction,
            "image_guidance_scale": image_guidance_scale,
            "text_guidance_scale": text_guidance_scale,
            "init_image_strength": init_image_strength,
            "start_frame_index": 0,
            "seed": str(seed),
        }
        if color_image_path:
            payload["selected_reference_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        payload["model_name"] = "generate_movement"
        result = await ws_client.call("generate-movement", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "movement", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 2. Animate with text (v1) ─────────────────────────────────────────────

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
        seed: int = 0,
    ) -> str:
        """Animate a pixel art character using a text action description (quick version).

        Args:
            reference_image_path: Character sprite to animate.
            action: Text description of animation e.g. "Walking", "Jump attack".
            view: side / low top-down / high top-down / none
            direction: north / east / south / west / none
        """
        b64_png = image_utils.path_to_png_b64(reference_image_path)
        payload = {
            "reference_image": {"base64": b64_png},
            "reference_image_size": {"width": width, "height": height},
            "action": action,
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "seed": str(seed),
        }
        payload["model_name"] = "generate_animate_with_text"
        result = await ws_client.call("generate-animate-with-text", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "animate_text", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 3. Animate with text v3 ───────────────────────────────────────────────

    @mcp.tool()
    async def animate_with_text_v3(
        reference_image_path: str,
        action: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        frame_count: int = 8,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Animate a pixel art character with text (v3 – higher quality, even frame count).

        Args:
            reference_image_path: Character sprite to animate.
            action: Text description of animation e.g. "Walking cycle".
            frame_count: Number of frames; must be even, range 4–16.
        """
        b64_rgba, w, h = image_utils.path_to_rgba_b64(reference_image_path)
        payload = {
            "first_frame": {"type": "rgba_bytes", "base64": b64_rgba, "width": w, "height": h},
            "action": action,
            "image_size": {"width": width, "height": height},
            "frame_count": frame_count,
            "no_background": no_background,
            "seed": str(seed),
        }
        payload["model_name"] = "generate_animate_with_text_v3"
        result = await ws_client.call("animate-with-text-v3", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "animate_text_v3", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 4. Skeleton-based animation ───────────────────────────────────────────

    @mcp.tool()
    async def animation_generate(
        action: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        description: str = "",
        view: str = "low top-down",
        direction: str = "south",
        n_images: int = 8,
        text_guidance_scale: float = 8.0,
        ai_freedom: int = 750,
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        template_name: str = "",
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a skeleton-driven animation sequence from text.

        Args:
            action: Animation type e.g. "walk", "run", "attack".
            n_images: Number of frames to generate (2–20).
            ai_freedom: 0 = strict template; 750 = default creative freedom.
            template_name: Optional character template e.g. "female-humanoid".
        """
        payload = {
            "action": action,
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "direction": direction,
            "n_images": n_images,
            "ai_freedom": ai_freedom,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "seed": str(seed),
            "isometric": False,
            "oblique_projection": False,
        }
        if template_name:
            payload["template_name"] = template_name
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        payload["model_name"] = "generate_animation"
        result = await ws_client.call("generate-animation", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "animation", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 5. Animate character/object ───────────────────────────────────────────

    @mcp.tool()
    async def animate_character_object(
        reference_image_path: str,
        action: str,
        output_dir: str,
        description: str = "",
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Animate a character or object (e.g. bouncing, exploding, spinning).

        Good for simple objects and VFX animations.

        Args:
            reference_image_path: Sprite or object image to animate.
            action: Free-text animation description e.g. "bouncing and then exploding into pieces".
            description: Optional additional description of the subject.
        """
        payload = {
            "display_reference_image": image_utils.path_to_png_b64(reference_image_path),
            "action": action,
            "description": description,
            "no_background": no_background,
            "seed": str(seed),
        }
        payload["model_name"] = "generate_animate_character_object"
        result = await ws_client.call("generate-animate-character-object", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "char_object_anim", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 6. Interpolation ──────────────────────────────────────────────────────

    @mcp.tool()
    async def interpolation_generate(
        from_image_path: str,
        to_image_path: str,
        output_dir: str,
        action: str = "transforming",
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        direction: str = "east",
        image_guidance_scale: float = 1.0,
        text_guidance_scale: float = 8.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate in-between frames interpolating from one sprite to another.

        Useful for morph animations, state transitions, death sequences etc.

        Args:
            from_image_path: Starting frame.
            to_image_path: Ending frame.
            action: Description of the transition e.g. "transforming", "dying".
        """
        payload = {
            "interpolation_from": image_utils.path_to_png_b64(from_image_path),
            "interpolation_to": image_utils.path_to_png_b64(to_image_path),
            "character": action,
            "action": action,
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "image_guidance_scale": image_guidance_scale,
            "text_guidance_scale": text_guidance_scale,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        payload["model_name"] = "generate_interpolation"
        result = await ws_client.call("generate-interpolation", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "interpolation", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 7. Interpolation v3 ───────────────────────────────────────────────────

    @mcp.tool()
    async def interpolation_v3_generate(
        start_image_path: str,
        end_image_path: str,
        output_dir: str,
        action: str = "transforming",
        frame_count: int = 8,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Generate interpolation frames between two images (v3 – higher quality).

        Args:
            start_image_path: First frame of the transition.
            end_image_path: Last frame of the transition.
            action: Description of transition e.g. "transforming", "melting".
            frame_count: Number of in-between frames (even number, 4–16).
        """
        payload = {
            "display_start_image": image_utils.path_to_png_b64(start_image_path),
            "display_end_image": image_utils.path_to_png_b64(end_image_path),
            "action": action,
            "frame_count": frame_count,
            "no_background": no_background,
            "seed": str(seed),
        }
        payload["model_name"] = "generate_interpolation_v3"
        result = await ws_client.call("generate-interpolation-v3", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "interpolation_v3", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 8. Interpolation Pro ──────────────────────────────────────────────────

    @mcp.tool()
    async def interpolation_pro_generate(
        start_image_path: str,
        end_image_path: str,
        output_dir: str,
        action: str = "transforming",
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Generate high-quality interpolation frames between two pixel art images (Pro).

        Args:
            start_image_path: First frame.
            end_image_path: Last frame.
            action: Description of the transition.
        """
        payload = {
            "display_start_image": image_utils.path_to_png_b64(start_image_path),
            "display_end_image": image_utils.path_to_png_b64(end_image_path),
            "action": action,
            "no_background": no_background,
            "seed": str(seed),
        }
        payload["model_name"] = "interpolation"
        result = await ws_client.call("generate-interpolation-pro", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, 64, 64, "interpolation_pro", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)
