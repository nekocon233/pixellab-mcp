"""Tools: character generation and skeleton-based animation."""
import json
from typing import Optional

from PIL import Image

from . import image_utils
from . import http_client


def register(mcp) -> None:

    # ── 1. Complete character (one-shot) ──────────────────────────────────────

    @mcp.tool()
    async def complete_character_generate(
        description: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        text_guidance_scale: float = 8.0,
        direction_type: str = "cardinal",
        outline: str = "selective outline",
        shading: str = "basic shading",
        detail: str = "low detail",
        proportions: str = "default",
        template_id: Optional[str] = None,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a complete character with all directional views.

        Produces multi-direction spritesheets in a single call.
        Max 128x128 per frame. Note: V2 generates rotation views only;
        use the animate_character tool separately for animations.

        Args:
            direction_type: cardinal (4-dir) or all (8-dir).
            proportions: default / chibi / cartoon / stylized / realistic_male / realistic_female / heroic.
            template_id: Optional template e.g. "mannequin", "bear", "cat", "dog", "horse", "lion".
        """
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "proportions": {"type": "preset", "name": proportions},
            "seed": seed,
        }
        if template_id:
            payload["template_id"] = template_id
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        endpoint = (
            "create-character-with-8-directions"
            if direction_type == "all"
            else "create-character-with-4-directions"
        )
        result = await http_client.call_async(endpoint, payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "complete_char", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 2. Estimate skeleton ──────────────────────────────────────────────────

    @mcp.tool()
    async def estimate_skeleton(
        image_path: str,
    ) -> str:
        """Estimate skeleton keypoints from a character image.

        Returns JSON keypoints that can be used with animate_with_skeleton
        or pose_generate tools.

        Args:
            image_path: Character image to extract skeleton from.
        """
        payload = {
            "image": {"base64": image_utils.path_to_png_b64(image_path)},
        }
        result = await http_client.call("estimate-skeleton", payload)
        return json.dumps(result, indent=2)

    # ── 3. Animate with skeleton ──────────────────────────────────────────────

    @mcp.tool()
    async def animate_with_skeleton(
        reference_image_path: str,
        skeleton_keypoints: str,
        output_dir: str,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        direction: str = "south",
        guidance_scale: float = 4.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Animate a character using skeleton pose control.

        Use estimate_skeleton to get keypoints, modify them, then animate.

        Args:
            reference_image_path: Character sprite to animate.
            skeleton_keypoints: JSON array of keypoint arrays (one per frame).
                Each keypoint: {"x": 0.5, "y": 0.3, "label": "NOSE", "z_index": 0}.
            guidance_scale: How strongly to follow the skeleton (1-20).
        """
        keypoints = json.loads(skeleton_keypoints)
        payload = {
            "reference_image": {"base64": image_utils.path_to_png_b64(reference_image_path)},
            "image_size": {"width": width, "height": height},
            "skeleton_keypoints": keypoints,
            "guidance_scale": guidance_scale,
            "view": view,
            "direction": direction,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call("animate-with-skeleton", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "skeleton_anim", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 4. Pose-based generation ──────────────────────────────────────────────

    @mcp.tool()
    async def pose_generate(
        skeleton_keypoints: str,
        output_dir: str,
        description: str = "",
        width: int = 128,
        height: int = 128,
        view: str = "low top-down",
        direction: str = "none",
        text_guidance_scale: float = 8.0,
        skeleton_guidance_scale: float = 1.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_path: Optional[str] = None,
    ) -> str:
        """Generate a character in a specific skeleton pose.

        Use estimate_skeleton to get keypoints from a reference, then generate
        a new character in that pose.

        Args:
            skeleton_keypoints: JSON array of keypoint objects (one frame).
                Use output from estimate_skeleton.
            description: Character description.
            skeleton_guidance_scale: How strictly to follow the skeleton (0-5).
        """
        keypoints = json.loads(skeleton_keypoints)
        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            "skeleton_keypoints": keypoints,
            "skeleton_guidance_scale": skeleton_guidance_scale,
            "text_guidance_scale": text_guidance_scale,
            "view": view,
            "direction": direction,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_path:
            payload["init_image"] = {"base64": image_utils.path_to_png_b64(init_image_path)}

        result = await http_client.call("create-image-bitforge", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pose", output_dir)
        return f"Saved {len(paths)} image(s):\n" + "\n".join(paths)

    # ── 5. Pose animation ─────────────────────────────────────────────────────

    @mcp.tool()
    async def pose_animation_generate(
        skeleton_keypoints_list: str,
        output_dir: str,
        reference_image_path: Optional[str] = None,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        direction: str = "south",
        guidance_scale: float = 4.0,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Generate a multi-frame animation driven by skeleton keypoints.

        Each set of keypoints defines the skeleton for the corresponding output frame.

        Args:
            skeleton_keypoints_list: JSON array of keypoint arrays (one array per frame).
                Example: [[{"x":0.5,"y":0.3,"label":"NOSE","z_index":0}, ...], [...]]
            reference_image_path: Optional style reference character.
            guidance_scale: Strength of skeleton constraints (1-20).
        """
        all_keypoints = json.loads(skeleton_keypoints_list)
        payload = {
            "image_size": {"width": width, "height": height},
            "skeleton_keypoints": all_keypoints,
            "guidance_scale": guidance_scale,
            "view": view,
            "direction": direction,
            "seed": seed,
        }
        if reference_image_path:
            payload["reference_image"] = {"base64": image_utils.path_to_png_b64(reference_image_path)}
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call("animate-with-skeleton", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pose_animation", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)
