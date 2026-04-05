"""Tools: complete character generation and pose manipulation."""
from typing import List, Optional

from . import image_utils
from . import ws_client


def register(mcp) -> None:

    # ── 1. Complete character (one-shot) ──────────────────────────────────────

    @mcp.tool()
    async def complete_character_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "high top-down",
        character_type: str = "bipedal-semi-chibi",
        text_guidance_scale: float = 8.0,
        animation_type: str = "walk",
        direction_type: str = "cardinal",
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "low detail",
        negative_description: str = "mixels. amateur. multiple. grainy background",
        seed: int = 0,
        south_reference_path: Optional[str] = None,
        north_reference_path: Optional[str] = None,
        east_reference_path: Optional[str] = None,
        south_east_reference_path: Optional[str] = None,
        north_east_reference_path: Optional[str] = None,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a complete animated character with all directions and animation frames.

        This is the fullest character generation tool – it produces multi-direction
        animated spritesheets in a single call.  Max 64×64 per frame.

        Args:
            character_type: bipedal-semi-chibi / bipedal-realistic / etc.
            animation_type: walk / run / etc.
            direction_type: cardinal (4-dir) / all (8-dir)
            south_reference_path: Optional south-facing reference image.
            north_reference_path: Optional north-facing reference image.
            east_reference_path: Optional east-facing reference image.
        """
        payload = {
            "description": description,
            "negative_description": negative_description,
            "character_type": character_type,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "animation_type": animation_type,
            "direction_type": direction_type,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "seed": str(seed),
            "vfx": False,
            "scale": 1,
            "head_scale": 1,
            "arms_scale": 1,
            "legs_scale": 1,
        }
        if south_reference_path:
            payload["south_reference_image"] = image_utils.path_to_png_b64(south_reference_path)
        if north_reference_path:
            payload["north_reference_image"] = image_utils.path_to_png_b64(north_reference_path)
        if east_reference_path:
            payload["east_reference_image"] = image_utils.path_to_png_b64(east_reference_path)
        if south_east_reference_path:
            payload["south_east_reference_image"] = image_utils.path_to_png_b64(south_east_reference_path)
        if north_east_reference_path:
            payload["north_east_reference_image"] = image_utils.path_to_png_b64(north_east_reference_path)
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)

        result = await ws_client.call("generate-one-shot", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "complete_char", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 2. Re-pose animation ──────────────────────────────────────────────────

    @mcp.tool()
    async def re_pose_animation(
        reference_image_path: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        direction: str = "south",
        guidance_scale: float = 3.0,
        init_image_strength: int = 300,
        isometric: bool = False,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Re-pose a character animation using skeleton pose control.

        Args:
            reference_image_path: Current animation frame to re-pose.
            view: low top-down / high top-down / side
            direction: north / east / south / west
            guidance_scale: How strongly to follow the pose constraints.
        """
        payload = {
            "selected_reference_frame": image_utils.path_to_png_b64(reference_image_path),
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "guidance_scale": guidance_scale,
            "init_image_strength": init_image_strength,
            "isometric": isometric,
            "oblique_projection": False,
            "use_inpainting": False,
            "use_init_image": init_image_path is not None,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)

        result = await ws_client.call("generate-re-pose-animation", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "re_pose", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 3. Pose-based generation ──────────────────────────────────────────────

    @mcp.tool()
    async def pose_generate(
        pose_image_path: str,
        output_dir: str,
        description: str = "",
        width: int = 128,
        height: int = 128,
        view: str = "low top-down",
        direction: str = "none",
        text_guidance_scale: float = 8.0,
        pose_guidance_scale: float = 1.0,
        no_background: bool = False,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate a character in the pose described by a pose/skeleton image.

        Args:
            pose_image_path: Pose skeleton image (can be from a pose editor or existing character).
            description: Character description.
            pose_guidance_scale: How strictly to follow the pose image (0.5 = loose, 2 = strict).
        """
        payload = {
            "pose_image": image_utils.path_to_png_b64(pose_image_path),
            "image_size": {"width": width, "height": height},
            "pose_image_size": {"width": 512, "height": 512},
            "text_guidance_scale": text_guidance_scale,
            "pose_guidance_scale": pose_guidance_scale,
            "view": view,
            "direction": direction,
            "no_background": no_background,
            "no_background_guidance_scale": 4,
            "view_direction": False,
            "view_direction_guidance_scale": 4,
            "pixelart_style_guidance_scale": 4,
            "init_image_strength": init_image_strength,
            "seed": str(seed),
        }
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)
        if init_image_path:
            payload["init_image"] = image_utils.path_to_png_b64(init_image_path)

        result = await ws_client.call("generate-general-pose", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pose", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 4. Pose animation ─────────────────────────────────────────────────────

    @mcp.tool()
    async def pose_animation_generate(
        pose_image_paths: List[str],
        output_dir: str,
        reference_image_path: Optional[str] = None,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        direction: str = "south",
        reference_direction: str = "automatic",
        pose_guidance_scale: float = 3.0,
        reference_guidance_scale: float = 1.0,
        init_image_strength: int = 300,
        isometric: bool = False,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a multi-frame animation driven by a sequence of pose images.

        Each pose image defines the skeleton for the corresponding output frame.

        Args:
            pose_image_paths: Ordered list of pose/skeleton images for each frame.
            reference_image_path: Optional style reference character.
            view: low top-down / high top-down / side
            direction: north / east / south / west
            reference_direction: automatic / south / east / etc.
            pose_guidance_scale: Strength of pose constraints.
            reference_guidance_scale: Strength of style reference.
        """
        pose_b64_list = [image_utils.path_to_png_b64(p) for p in pose_image_paths]
        payload = {
            "pose_images": pose_b64_list,
            "image_size": {"width": width, "height": height},
            "view": view,
            "direction": direction,
            "reference_direction": reference_direction,
            "pose_guidance_scale": pose_guidance_scale,
            "reference_guidance_scale": reference_guidance_scale,
            "guidance_scale": pose_guidance_scale,
            "init_image_strength": init_image_strength,
            "isometric": isometric,
            "oblique_projection": False,
            "use_inpainting": False,
            "seed": str(seed),
        }
        if reference_image_path:
            payload["selected_reference_image"] = image_utils.path_to_png_b64(reference_image_path)
        if color_image_path:
            payload["color_image"] = image_utils.path_to_png_b64(color_image_path)

        result = await ws_client.call("generate-pose-animation", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pose_animation", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)
