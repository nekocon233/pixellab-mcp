"""Tools: map object and multi-direction object generation."""
import json
from typing import List, Optional

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
        background_image_path: Optional[str] = None,
        inpainting: Optional[str] = None,
    ) -> str:
        """Generate a map object (tree, rock, chest, etc.) for top-down games.

        Args:
            description: Object description e.g. "oak tree", "treasure chest", "stone wall".
            width/height: Image size (32-400).
            view: low top-down / high top-down / side.
            no_background: True = transparent background.
            background_image_path: Optional background image to place the object on.
            inpainting: JSON inpainting config. Supports mask (custom), oval, or rectangle types.
                        Example: '{"type": "oval"}' or '{"type": "rectangle", "padding": 16}'.
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
        if background_image_path:
            payload["background_image"] = {"base64": image_utils.path_to_png_b64(background_image_path)}
        if inpainting:
            payload["inpainting"] = json.loads(inpainting)

        result = await http_client.call_async("map-objects", payload)
        images = image_utils.extract_images(result)
        paths = image_utils.save_response_images(images, width, height, "map_object", output_dir)
        return f"Saved {len(paths)} object(s):\n" + "\n".join(paths)

    # ── 2. New Objects API (POST /objects) ────────────────────────────────────

    @mcp.tool()
    async def create_object(
        description: str,
        output_dir: str,
        directions: int = 8,
        width: int = 64,
        height: int = 64,
        view: str = "low top-down",
        no_background: bool = True,
        seed: int = 0,
        reference_image_path: Optional[str] = None,
        style_image_paths: Optional[List[str]] = None,
        object_view: Optional[str] = None,
        n_frames: int = 1,
        item_descriptions: Optional[str] = None,
        variation_of: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> str:
        """Create a pixel art object using the new Objects pipeline.

        1-direction mode uses the consistent-style pipeline (good for static map decorations).
        8-direction mode uses the rotations pipeline (good for rotatable items).

        Returns object_id and background_job_id. Poll get_object_status() for results.

        Args:
            directions: 1 (consistent-style) or 8 (all rotations).
            width/height: Image size (32-256).
            view: low top-down / high top-down / side.
            n_frames: Candidate frames (1, 4, 16, 64). n_frames>1 returns review status.
            reference_image_path: South-facing reference for 8-direction mode.
            style_image_paths: Style references for 1-direction (consistent-style) mode.
            object_view: Default-style category when no style_images provided.
            item_descriptions: JSON array of per-frame descriptions for consistent-style multi-frame packs.
            variation_of: Object ID this is a variation of (groups them together).
            group_id: Group ID for related objects.
        """
        payload = {
            "description": description,
            "directions": directions,
            "image_size": {"width": width, "height": height},
            "view": view,
            "no_background": no_background,
            "n_frames": n_frames,
            "seed": seed,
        }
        if reference_image_path:
            payload["reference_image"] = {"base64": image_utils.path_to_png_b64(reference_image_path)}
        if style_image_paths:
            from PIL import Image as _Image
            payload["style_images"] = [
                {"image": {"base64": image_utils.path_to_png_b64(p)},
                 "size": {"width": _Image.open(p).size[0], "height": _Image.open(p).size[1]}}
                for p in style_image_paths
            ]
        if object_view:
            payload["object_view"] = object_view
        if item_descriptions:
            payload["item_descriptions"] = json.loads(item_descriptions)
        if variation_of:
            payload["variation_of"] = variation_of
        if group_id:
            payload["group_id"] = group_id

        result = await http_client.call_async("objects", payload)
        return json.dumps(result, indent=2)

    # ── 4. Animate object ────────────────────────────────────────────────────

    @mcp.tool()
    async def animate_object(
        object_id: str,
        direction: str,
        animation_description: str,
        frame_count: int = 8,
        no_background: bool = True,
        animation_name: Optional[str] = None,
        wait_for_source: bool = True,
    ) -> str:
        """Animate an existing object in a specific direction.

        Returns animation_id and background_job_id immediately (async processing).

        Args:
            object_id: UUID of a completed object.
            direction: south / south-west / west / north-west / north / north-east / east / south-east.
            animation_description: e.g. "idle breathing", "spin".
            frame_count: Even number 4-16.
            wait_for_source: When True, polls up to 30s waiting for source object to reach completed status.
        """
        payload = {
            "object_id": object_id,
            "direction": direction,
            "animation_description": animation_description,
            "frame_count": frame_count,
            "no_background": no_background,
            "wait_for_source": wait_for_source,
        }
        if animation_name:
            payload["animation_name"] = animation_name

        result = await http_client.call_async("animate-object", payload)
        return json.dumps(result, indent=2)

    # ── 5. Vary object ───────────────────────────────────────────────────────

    @mcp.tool()
    async def vary_object(
        object_id: str,
        edit_description: str,
        no_background: bool = True,
        seed: int = 0,
    ) -> str:
        """Create a variation of an existing object by applying a text edit.

        The new object is grouped with the source object.

        Args:
            object_id: UUID of the source (completed) object.
            edit_description: Text edit to apply e.g. "make it golden", "add rust".
        """
        payload = {
            "object_id": object_id,
            "edit_description": edit_description,
            "no_background": no_background,
            "seed": seed,
        }
        result = await http_client.call_async("vary-object", payload)
        return json.dumps(result, indent=2)

    # ── 6. Select frames from a review object ────────────────────────────────

    @mcp.tool()
    async def select_object_frames(
        object_id: str,
        indices: str,
        common_tag: Optional[str] = None,
    ) -> str:
        """Promote selected frames of a review-status object to completed objects.

        Use after create_object() returns status='review' (i.e. n_frames > 1).

        Args:
            object_id: UUID of the review-status object.
            indices: JSON array of 0-based frame indices to keep e.g. "[0, 2]".
            common_tag: Optional tag applied to every newly-created object.
        """
        payload = {"indices": json.loads(indices)}
        if common_tag:
            payload["common_tag"] = common_tag
        result = await http_client.call_async(f"objects/{object_id}/select-frames", payload)
        return json.dumps(result, indent=2)

    # ── 7. Dismiss a review object ───────────────────────────────────────────

    @mcp.tool()
    async def dismiss_object_review(
        object_id: str,
    ) -> str:
        """Dismiss a review-status object without saving any frames.

        Args:
            object_id: UUID of the review-status object to discard.
        """
        result = await http_client.call_async(f"objects/{object_id}/dismiss-review", {})
        return json.dumps(result, indent=2)
