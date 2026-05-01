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
        isometric: bool = False,
        force_colors: bool = False,
        mode: Optional[str] = None,
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
            isometric: True = generate in isometric view.
            force_colors: True = force use of colors from color_image.
            mode: "standard" (template-based, 1 gen) or "pro" (AI reference, 20-40 gens, higher quality).
                Pro mode ignores outline, shading, detail, proportions, text_guidance_scale.
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
            "isometric": isometric,
            "force_colors": force_colors,
            "seed": seed,
        }
        if mode:
            payload["mode"] = mode
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
            "image": {"base64": image_utils.path_to_png_b64(image_path), "type": "base64"},
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
        isometric: bool = False,
        oblique_projection: bool = False,
        init_image_strength: int = 300,
        seed: int = 0,
        color_image_path: Optional[str] = None,
        init_image_paths: Optional[str] = None,
        inpainting_image_paths: Optional[str] = None,
        mask_image_paths: Optional[str] = None,
    ) -> str:
        """Animate a character using skeleton pose control.

        Use estimate_skeleton to get keypoints, modify them, then animate.

        Args:
            reference_image_path: Character sprite to animate.
            skeleton_keypoints: JSON array of keypoint arrays (one per frame).
                Each keypoint: {"x": 0.5, "y": 0.3, "label": "NOSE", "z_index": 0}.
            guidance_scale: How strongly to follow the skeleton (1-20).
            isometric: True = isometric view.
            oblique_projection: True = oblique projection.
            init_image_paths: JSON array of file paths for initial images.
            inpainting_image_paths: JSON array of file paths for inpainting images.
            mask_image_paths: JSON array of file paths for mask images.
        """
        keypoints = json.loads(skeleton_keypoints)
        payload = {
            "reference_image": {"base64": image_utils.path_to_png_b64(reference_image_path), "type": "base64", "format": "png"},
            "image_size": {"width": width, "height": height},
            "skeleton_keypoints": keypoints,
            "guidance_scale": guidance_scale,
            "view": view,
            "direction": direction,
            "isometric": isometric,
            "oblique_projection": oblique_projection,
            "init_image_strength": init_image_strength,
            "seed": seed,
        }
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}
        if init_image_paths:
            payload["init_images"] = [
                {"base64": image_utils.path_to_png_b64(p)} for p in json.loads(init_image_paths)
            ]
        if inpainting_image_paths:
            payload["inpainting_images"] = [
                {"base64": image_utils.path_to_png_b64(p)} for p in json.loads(inpainting_image_paths)
            ]
        if mask_image_paths:
            payload["mask_images"] = [
                {"base64": image_utils.path_to_png_b64(p)} for p in json.loads(mask_image_paths)
            ]

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
            payload["reference_image"] = {"base64": image_utils.path_to_png_b64(reference_image_path), "type": "base64", "format": "png"}
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call("animate-with-skeleton", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "pose_animation", output_dir)
        return f"Saved {len(paths)} frame(s):\n" + "\n".join(paths)

    # ── 6. Animate character (template-based) ────────────────────────────────

    @mcp.tool()
    async def animate_character(
        character_id: str,
        action_description: str = "",
        animation_name: Optional[str] = None,
        description: Optional[str] = None,
        mode: str = "v3",
        template_animation_id: Optional[str] = None,
        frame_count: int = 8,
        directions: Optional[str] = None,
        isometric: bool = False,
        text_guidance_scale: Optional[float] = None,
        outline: Optional[str] = None,
        shading: Optional[str] = None,
        detail: Optional[str] = None,
        force_colors: bool = False,
        seed: int = 0,
        color_image_path: Optional[str] = None,
    ) -> str:
        """Animate an existing character created via complete_character_generate.

        Args:
            character_id: UUID of the character to animate.
            action_description: Action e.g. "walking", "jumping", "attack".
                Required for custom mode (when template_animation_id is omitted).
            mode: "template" (skeleton-based, 1 gen/direction), "v3" (custom, frame_count
                control), or "pro" (highest quality, 20-40 gen/direction).
            template_animation_id: Required for template mode. Available: "angry",
                "attack", "attack-back", "attack-left", "attack-right", "backflip",
                "bark", "breathing-idle", "cross-punch", "crouched-walking", etc.
            frame_count: Number of animation frames (4-16, even). v3 mode only.
            directions: JSON array of directions to animate e.g. '["south", "north"]'.
                Defaults to south only for custom modes, all directions for template mode.
            animation_name: Optional name for the animation.
            description: Override character description.
            isometric: Generate in isometric view.
            text_guidance_scale: How closely to follow text (template mode only).
            outline/shading/detail: Override style (template mode only, uses character's original if not specified).
            force_colors: Force use of colors from color_image.
        """
        import json as _json
        payload: dict = {
            "character_id": character_id,
            "mode": mode,
            "frame_count": frame_count,
            "isometric": isometric,
            "force_colors": force_colors,
            "seed": seed,
        }
        if action_description:
            payload["action_description"] = action_description
        if animation_name:
            payload["animation_name"] = animation_name
        if description:
            payload["description"] = description
        if template_animation_id:
            payload["template_animation_id"] = template_animation_id
        if directions:
            payload["directions"] = _json.loads(directions)
        if text_guidance_scale is not None:
            payload["text_guidance_scale"] = text_guidance_scale
        if outline:
            payload["outline"] = outline
        if shading:
            payload["shading"] = shading
        if detail:
            payload["detail"] = detail
        if color_image_path:
            payload["color_image"] = {"base64": image_utils.path_to_png_b64(color_image_path)}

        result = await http_client.call_async("animate-character", payload)
        return _json.dumps(result, indent=2)
